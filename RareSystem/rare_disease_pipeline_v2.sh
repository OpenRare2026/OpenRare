#!/bin/bash
#
# Rare Disease Analysis Pipeline v2
# 流程: HPO RAG -> VEP(带HPO) -> 表型-HPO评分 -> PPI -> Report
#

# set -e

# ==================== 配置 ====================
HPO_RAG_URL="http://localhost:9002"
# VEP_URL="http://172.27.206.113:8000"
VEP_URL="http://localhost:8000"
PHENOTYPE_URL="http://localhost:7002"
PPI_URL="http://localhost:9000"
REPORT_URL="http://localhost:7000"
LIFTOVER_URL="http://localhost:2850"

POLL_INTERVAL=60
MAX_WAIT=21600 # 6小时 = 21600秒

CURL_TIMEOUT=30
CONNECT_TIMEOUT=10

PYTHON="python3"


LIFTOVER_POLL_INTERVAL=60 # 考虑到坐标转换耗时较长，设定每 1 分钟（60秒）轮询一次

# ==================== 工具函数 ====================

# ==================== 工具函数 (修复流劫持版) ====================

log_info() {
    # 加上 >&2，确保日志永远打向终端屏幕，绝对不会被外层变量捕获拦截
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1" >&2
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1" >&2
}

log_success() {
    echo "[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1" >&2
}

log_warning() {
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') $1" >&2
}

usage() {
    cat << EOF
用法: $0 -v <vcf_file> -t "<描述文本>" [-o <输出目录>]

参数:
  -v <vcf_file>    输入的VCF文件路径（必填）
  -t "<描述文本>"   患者症状描述文本（必填）
  -o <输出目录>    输出目录（默认: ./rare_disease_output_<时间戳>）
  -h               显示帮助信息

示例:
  $0 -v /path/to/sample.vcf -t "患者表现为肌无力、运动发育迟缓"
  $0 -v /path/to/sample.vcf -t "aml" -o ./output_case1

EOF
    exit 1
}

json_get() {
    local json="$1"
    local key="$2"
    local default="${3:-}"
    echo "$json" | $PYTHON -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    keys = '$key'.split('.')
    for k in keys:
        if isinstance(data, dict):
            data = data.get(k)
        else:
            data = None
            break
    if data is None or data == 'null':
        print('$default')
    else:
        print(data)
except:
    print('$default')
" 2>/dev/null
}

check_service() {
    local url=$1
    curl -s --connect-timeout 5 --max-time 10 "${url}" >/dev/null 2>&1
}

wait_for_job() {
    local url=$1
    local service_name=$2
    local elapsed=0
    
    while [ $elapsed -lt $MAX_WAIT ]; do
        local response
        response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time $CURL_TIMEOUT "${url}" 2>/dev/null) || {
            log_warning "${service_name} 查询失败，重试中..."
            sleep $POLL_INTERVAL
            elapsed=$((elapsed + POLL_INTERVAL))
            continue
        }
        
        local status
        status=$(json_get "$response" "status" "")
        
        case "$status" in
            completion|completed)
                log_success "${service_name} 任务完成"
                echo "$response"
                return 0
                ;;
            failure|failed)
                local error_msg=$(json_get "$response" "message" "$(json_get "$response" "error" "未知错误")")
                log_error "${service_name} 任务失败: $error_msg"
                return 1
                ;;
            queuing|running)
                log_info "${service_name} 任务状态: $status, 等待中..."
                ;;
            *)
                log_info "${service_name} 任务状态: ${status:-未知}, 等待中..."
                ;;
        esac
        
        sleep $POLL_INTERVAL
        elapsed=$((elapsed + POLL_INTERVAL))
    done
    
    log_error "${service_name} 任务超时"
    return 1
}

# ==================== 服务调用函数 ====================



# Step 1: HPO RAG服务 - 从描述文本提取HPO词条（修正版）
# Step 1: HPO RAG服务 - 从描述文本提取HPO词条（修正版）
# Step 1: HPO RAG服务 - 彻底解决 set -e 崩溃与空变量卡死问题
run_hpo_rag() {
    local text=$1
    local output_dir=$2
    
    log_info "提交HPO RAG任务: 从描述文本提取HPO词条"
    
    local escaped_text=$(echo "$text" | $PYTHON -c "
import sys, json
print(json.dumps(sys.stdin.read().strip())[1:-1])
")
    
    # 允许在 curl 和初步解析期间失败而不崩溃
    set +e
    
    local response
    response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time 120 -X POST "${HPO_RAG_URL}/api/v1/extract" \
        -H 'Content-Type: application/json' \
        -d "{\"notes\": [{\"patient_id\": \"1\", \"clinical_note\": \"${escaped_text}\"}]}" 2>/dev/null)
        
    local curl_status=$?
    
    if [ $curl_status -ne 0 ] || [ -z "$response" ]; then
        set -e # 恢复网络限制
        log_error "严重错误: 无法连接到 HPO RAG 网络接口 (curl 退出码: $curl_status)"
        return 1
    fi

    # 严格解析 job_id
    local job_id
    job_id=$(echo "$response" | $PYTHON -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    print(data.get('job_id', ''))
except Exception as e:
    pass
" 2>/dev/null)

    set -e # 恢复命令严格模式
    
    # 如果抓不到 job_id，说明第一步请求就报错了，立即把后端返回的报错打印出来！
    if [ -z "$job_id" ]; then
        log_error "错误：HPO RAG 任务提交失败，未能从响应中拿到 job_id！"
        echo "====================================================" >&2
        echo "【HPO 服务接口返回的原始数据如下】:" >&2
        echo "$response" >&2
        echo "====================================================" >&2
        return 1
    fi
    
    log_info "HPO RAG任务成功提交！任务ID: $job_id"
    log_info "开始每 ${POLL_INTERVAL}s 进行一次状态轮询..."
    
    local elapsed=0
    local final_result=""
    local status=""
    
    while [ $elapsed -lt $MAX_WAIT ]; do
        # 轮询时也使用临时允许失败模式，防止偶发网络抖动导致整个管道挂掉
        set +e
        local status_response
        status_response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time $CURL_TIMEOUT "${HPO_RAG_URL}/runs/${job_id}" 2>/dev/null)
        
        status=$(echo "$status_response" | $PYTHON -c "
import sys, json
try:
    print(json.loads(sys.stdin.read()).get('status', ''))
except:
    print('unknown_json_error')
" 2>/dev/null)
        set -e
        
        # 强制用标准错误（>&2）把所有轮询明细轰炸到屏幕上
        echo "------------------------------------------------------------" >&2
        log_info "[RAG轮询耗时 ${elapsed}s] 当前状态: [$status]"
        echo "[当前响应JSON]: $status_response" >&2
        echo "------------------------------------------------------------" >&2
        
        if [ "$status" = "completed" ] || [ "$status" = "completion" ]; then
            log_success "HPO RAG 任务执行完成！"
            final_result="$status_response"
            break
        elif [ "$status" = "failure" ] || [ "$status" = "failed" ]; then
            log_error "HPO RAG 任务后端返回明确失败状态。"
            final_result="$status_response"
            break
        fi
        
        sleep $POLL_INTERVAL
        elapsed=$((elapsed + POLL_INTERVAL))
    done
    
    if [ -z "$final_result" ]; then
        log_error "HPO RAG 任务轮询超时。"
        return 1
    fi
    
    local hpo_file="${output_dir}/hpo_terms.txt"
    
    # 抽取并解析最终匹配的 HPO 词条
    echo "$final_result" | $PYTHON -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    results = data.get('results', [])
    if isinstance(results, list):
        hpo_ids = [r.get('hpo_id') for r in results if isinstance(r, dict) and r.get('hpo_id') and r.get('hpo_id') != 'No Candidate Fit']
        for h in hpo_ids:
            print(h)
except Exception as e:
    print(f'解析报错: {e}', file=sys.stderr)
" > "$hpo_file" 2>/dev/null || true
    
    # 正则保底方案
    if [ ! -s "$hpo_file" ]; then
        echo "$final_result" | grep -oE 'HP:[0-9]+' | sort -u > "$hpo_file" || true
    fi
    
    if [ -s "$hpo_file" ]; then
        log_success "HPO词条成功提取，已写入: $hpo_file"
        echo "【提取到的 HPO 列表如下】:" >&2
        cat "$hpo_file" >&2
    else
        log_warning "警告：该案例未检测到任何有效的 HPO 词条。"
    fi
    
    # 唯独这行标准输出用于被主流程变量捕获
    echo "$hpo_file"
}



run_liftover() {
    local vcf_file=$1
    local output_dir=$2
    local sample_name=$3  # 可选参数：可以传入样本名作为 run_name
    
    # 默认 run_name 处理
    if [ -z "$sample_name" ]; then
        sample_name="liftover_job"
    fi

    log_info "准备提交 VCF Liftover 任务..."
    log_info "检查输入 VCF 文件是否存在: $vcf_file"
    if [ ! -f "$vcf_file" ]; then
        log_error "严重错误：Liftover 输入文件不存在！路径: $vcf_file"
        return 1
    fi

    # 1. 异步提交任务
    log_info "正在向 ${LIFTOVER_URL}/runs 异步上传并创建坐标转换任务 (assembly=auto, normalize=true)..."
    
    set +e # 临时关闭严格模式，手动捕捉网络响应
    local response=""
    response=$(curl -s -X POST "${LIFTOVER_URL}/runs" \
        -F "file=@${vcf_file}" \
        -F "run_name=${sample_name}" \
        -F "assembly=auto" \
        -F "normalize=true" 2>/dev/null)
    local curl_status=$?
    set -e # 恢复严格模式

    if [ $curl_status -ne 0 ]; then
        log_error "严重错误：Liftover 任务提交失败！curl 无法建立连接，网络退出码: $curl_status"
        return 1
    fi

    if [ -z "$response" ]; then
        log_error "严重错误：Liftover 服务器未返回任何数据！请检查 113 服务器的 2850 端口或容器状态。"
        return 1
    fi

    # 解析 job_id
    local job_id
    job_id=$(echo "$response" | $PYTHON -c "
import sys, json
try:
    print(json.loads(sys.stdin.read()).get('job_id', ''))
except:
    pass
" 2>/dev/null)

    # 打印提交详情备查
    echo "==================== LIFTOVER SUBMISSION ====================" >&2
    log_info "【1. 输入客户端 VCF 文件】: $vcf_file"
    if [ -n "$job_id" ]; then
        log_success "【2. 成功创建 Liftover Job ID】: $job_id"
    else
        log_error "【2. 创建 Liftover 任务失败】: 未能在响应体中解析出 job_id"
    fi
    log_info "【3. 任务初始化 原始Response】:"
    log_info "$response" 
    echo "=============================================================" >&2

    if [ -z "$job_id" ]; then
        log_error "由于未获取到有效 Job ID，Liftover 流程被迫终止。"
        return 1
    fi

    # 2. 状态轮询监控
    log_info "成功通过断路检查。进入状态轮询（每隔 ${LIFTOVER_POLL_INTERVAL} 秒盘点一次状态）..."
    local elapsed=0
    local final_status_response=""

    while [ $elapsed -lt $MAX_WAIT ]; do
        set +e
        local status_response=""
        status_response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time $CURL_TIMEOUT "${LIFTOVER_URL}/runs/${job_id}" 2>/dev/null)
        
        local status=""
        status=$(echo "$status_response" | $PYTHON -c "
import sys, json
try:
    print(json.loads(sys.stdin.read()).get('status', ''))
except:
    print('unknown_json_error')
" 2>/dev/null)
        set -e

        # 实时打印轮询状态到屏幕（不污染标准输出）
        log_info "[Liftover 耗时 $((elapsed / 60)) 分钟] 当前状态字: [$status]"

        case "$status" in
            completion)
                log_success "Liftover 异步任务在后台圆满完成！"
                final_status_response="$status_response"
                log_info "你可以通过此链接查看完整日志: ${LIFTOVER_URL}/runs/${job_id}/log"
                log_info "$status_response"
                break
                ;;
            failure)
                echo "==================== LIFTOVER RUN ERROR ====================" >&2
                log_error "Liftover 任务在后台执行失败！"
                # 从响应体中提取具体的错误信息
                local err_msg
                err_msg=$(echo "$status_response" | $PYTHON -c "import sys, json; print(json.loads(sys.stdin.read()).get('error', '未知后端错误'))" 2>/dev/null)
                log_error "后端返回的错误原因: $err_msg"
                log_info "你可以通过此链接查看完整日志: ${LIFTOVER_URL}/runs/${job_id}/log"
                echo "============================================================" >&2
                return 1
                ;;
            queuing|running)
                # 处于排队或运行状态，静候下一次轮询
                ;;
            *)
                log_warning "捕捉到未预期的状态字 [$status]，继续观测..."
                ;;
        esac

        sleep $LIFTOVER_POLL_INTERVAL
        elapsed=$((elapsed + LIFTOVER_POLL_INTERVAL))
    done

    if [ -z "$final_status_response" ]; then
        log_error "Liftover 任务轮询超时，超过了设定的最大等待时间：$MAX_WAIT 秒"
        return 1
    fi

    # 3. 结果下载与校验
    # 根据文档推荐（第11节与22节）：后续分析优先推荐使用包含了规范化 indel 表示和左对齐结果的 norm VCF。
    local local_norm_vcf="${output_dir}/${sample_name}.grch38.norm.vcf.gz"
    
    log_info "正在从 113 服务器下载经过规范化(bcftools norm)后的 GRCh38 VCF 文件..."
    set +e
    curl -L -s --connect-timeout $CONNECT_TIMEOUT --max-time 1200 \
        -o "$local_norm_vcf" "${LIFTOVER_URL}/runs/${job_id}/download/norm"
    set -e

    if [ -s "$local_norm_vcf" ]; then
        log_success "GRCh38 规范化 VCF 下载成功，本地存储路径: $local_norm_vcf"
        
        # 根据文档第 22 节说明，目前没有单独的 .tbi 下载接口，在本地客户端直接执行 tabix 重新构建索引
        # log_info "正在本地为生成的 VCF 构建 tabix 索引..."
        # tabix -f -p vcf "$local_norm_vcf"
        # log_success "Tabix 索引构建完成！(.tbi)"
    else
        log_error "严重错误：未能成功下载规范化 VCF 文件，或文件内容为空！"
        return 1
    fi

    local vcf_return="${output_dir}/grch38.norm.vcf"

    # 判断是否为.gz文件
    if [[ "$local_norm_vcf" == *.gz ]]; then
        log_info "检测到.gz文件，正在解压缩..."
        
        # 解压为a.vcf文件
        gunzip -c "$local_norm_vcf" > "$vcf_return"
        
        # 检查解压是否成功
        if [ $? -eq 0 ]; then
            log_success "成功: 文件已解压为 $vcf_return"
        else
            log_error "错误: 解压失败"
            exit 1
        fi
    else
        log_error "错误: 文件 '$local_norm_vcf' 不是.gz文件"
        exit 1
    fi

    # 唯独这行标准输出，允许被外层的主程序变量（如 liftover_csv=$(run_liftover ...)）安全捕获
    echo "$vcf_return"
}

# Step 2: VEP服务 - 优化首轮提交信息的完整打印
# Step 2: VEP服务 - 彻底修复空返回流向轮询的Bug
# Step 2: VEP服务 - 彻底修复空返回流向轮询的Bug
run_vep() {
    local vcf_file=$1
    local hpo_file=$2
    local output_dir=$3
    
    log_info "准备提交 VEP 任务..."
    log_info "检查输入 VCF 文件是否存在: $vcf_file"
    if [ ! -f "$vcf_file" ]; then
        log_error "错误：VEP 输入文件不存在！路径: $vcf_file"
        return 1
    fi
    
    local hpo_ids=""
    if [ -s "$hpo_file" ]; then
        hpo_ids=$(cat "$hpo_file" | tr '\n' ',' | sed 's/,$//')
        log_info "关联传参的 HPO 词条: $hpo_ids"
    fi
    
    # 临时关闭 set -e，我们要手动、敏锐地捕捉 curl 的网络状态
    set +e
    
    local response=""
    if [ -n "$hpo_ids" ]; then
        log_info "正在向 ${VEP_URL}/runs 异步提交 VCF (带 HPO)..."
        response=$(curl -s -X POST "${VEP_URL}/runs" \
            -F "file=@${vcf_file}" \
            -F "hgvs=true" \
            -F "fork=32" \
            -F "hpo_id=${hpo_ids}" \
            -F "top_n_hpo_tissues=3" 2>/dev/null)
    else
        log_warning "未发现可用 HPO 词条，将使用默认无 HPO 模式提交 VEP"
        response=$(curl -s -X POST "${VEP_URL}/runs" \
            -F "file=@${vcf_file}" \
            -F "hgvs=true" \
            -F "fork=8" 2>/dev/null)
    fi
    
    local curl_status=$?
    
    # 恢复严格模式
    # set -e
    
    # 【核心铁腕断路机制 1】如果 curl 本身网络超时或崩了
    if [ $curl_status -ne 0 ]; then
        log_error "严重错误：VEP 任务提交失败！curl 无法建立连接，网络退出码: $curl_status"
        return 1
    fi
    
    # 【核心铁腕断路机制 2】如果服务器返回了完全空的内容
    if [ -z "$response" ]; then
        log_error "严重错误：VEP 服务器未返回任何数据（返回体为空）！请检查 VEP 服务端容器/进程是否存活。"
        return 1
    fi
    
    # 解析 job_id
    local job_id
    job_id=$(echo "$response" | $PYTHON -c "
import sys, json
try:
    print(json.loads(sys.stdin.read()).get('job_id', ''))
except:
    pass
" 2>/dev/null)
    
    # 【核心修改点】严格按照要求，在拿到响应的第一时间无视任何异常直接进行全要素打印
    echo "==================== VEP SUBMISSION DETAILS ====================" >&2
    log_info "【1. 输入 VCF 文件位置】: $vcf_file"
    if [ -n "$job_id" ]; then
        log_success "【2. 成功获取 VEP Job ID】: $job_id"
    else
        log_error "【2. 获取 VEP Job ID 失败】: 响应体中不包含有效的 job_id 字段！"
    fi
    log_info "【3. 第一次提交的 原始Response】:"
    echo "$response" | $PYTHON -m json.tool 2>/dev/null || echo "$response" >&2
    echo "================================================================" >&2
    
    # 【核心铁腕断路机制 3】如果 job_id 为空，绝对不允许进入下方的 5 分钟轮询，直接熔断
    if [ -z "$job_id" ]; then
        log_error "错误：因未能获取到有效的 Job ID，VEP 流程被迫终止。请根据上方打印的【原始Response】排查后端服务。"
        return 1
    fi
    
    log_info "成功通过断路检查。开始进入 VEP 状态监控（每隔 3 分钟检查并打印一次查询 JSON）..."
    
    local vep_poll_interval=180 # 3分钟 = 180秒
    local elapsed=0
    local final_response=""
    
    while [ $elapsed -lt $MAX_WAIT ]; do
        set +e
        local status_response
        status_response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time $CURL_TIMEOUT "${VEP_URL}/runs/${job_id}" 2>/dev/null)
        
        local status
        status=$(echo "$status_response" | $PYTHON -c "
import sys, json
try:
    print(json.loads(sys.stdin.read()).get('status', ''))
except:
    print('unknown_json_error')
" 2>/dev/null)
        set -e
        
        echo "============================================================" >&2
        log_info "[VEP轮询耗时 $((elapsed / 60)) 分钟] 当前状态字: [$status]"
        log_info "[当前 VEP 查询响应 JSON]:" 
        log_info "$status_response"  
        echo "============================================================" >&2
        
        case "$status" in
            completion|completed)
                log_success "VEP 任务后台执行完成！"
                final_response="$status_response"
                break
                ;;
            failure|failed)
                local error_msg=$(echo "$status_response" | $PYTHON -c "import sys, json; print(json.loads(sys.stdin.read()).get('message', '未知后端错误'))" 2>/dev/null)
                log_error "VEP 任务在后台运行失败: $error_msg"
                return 1
                ;;
            queuing|running)
                log_info "VEP 任务仍在排队或计算中，将在 3 分钟后进行下一次状态盘点..."
                ;;
            *)
                local error_msg=$(echo "$status_response" | $PYTHON -c "import sys, json; print(json.loads(sys.stdin.read()).get('message', '未知后端错误'))" 2>/dev/null)
                log_error "VEP 任务在后台运行失败: $error_msg"
                return 1
                ;;
        esac
        
        sleep $vep_poll_interval
        elapsed=$((elapsed + vep_poll_interval))
    done
    
    local csv_file="${output_dir}/vep_output.csv"
    log_info "正在从云端下载最终的 VEP 注释 CSV 文件..."
    
    curl -s --connect-timeout $CONNECT_TIMEOUT --max-time 600 -o "$csv_file" "${VEP_URL}/runs/${job_id}/result"
    
    if [ -s "$csv_file" ]; then
        log_success "VEP 注释数据下载成功，已安全存储至: $csv_file ($(wc -l < "$csv_file") 行)"
    else
        log_error "错误：未能成功下载 VEP 结果文件或文件内容为空！"
        return 1
    fi
    
    # echo "$csv_file"
}

# Step 3: 表型-HPO评分模块
run_phenotype_score() {
    local vep_csv=$1
    local hpo_file=$2
    local output_dir=$3
    
    log_info "提交表型-HPO评分任务"
    
    local response
    response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time $CURL_TIMEOUT -X POST "${PHENOTYPE_URL}/runs" \
        -F "file=@${vep_csv}" \
        -F "hpo_file=@${hpo_file}" \
        -F "hgvs=true" 2>/dev/null)
    
    local job_id
    job_id=$(json_get "$response" "uid" "$(json_get "$response" "job_id" "")")
    
    if [ -z "$job_id" ]; then
        log_error "表型-HPO评分任务提交失败: $response"
        return 1
    fi
    
    log_info "表型-HPO评分任务ID: $job_id"
    
    wait_for_job "${PHENOTYPE_URL}/runs/${job_id}" "表型-HPO评分" || return 1
    
    local gene_csv="${output_dir}/gene_phenotype_score.csv"
    local variant_csv="${output_dir}/variant_phenotype_score.csv"
    
    curl -s --connect-timeout $CONNECT_TIMEOUT --max-time 300 -o "$gene_csv" "${PHENOTYPE_URL}/runs/${job_id}/files/gene_phenotype_score.csv"
    curl -s --connect-timeout $CONNECT_TIMEOUT --max-time 300 -o "$variant_csv" "${PHENOTYPE_URL}/runs/${job_id}/files/variant_phenotype_score.csv"
    
    log_success "表型评分结果已保存: $gene_csv, $variant_csv"
    echo "${gene_csv}|${variant_csv}"
}

# Step 4: PPI服务
run_ppi() {
    local gene_phenotype_csv=$1
    local vep_csv=$2
    local hpo_file=$3
    local output_dir=$4
    
    log_info "提交PPI任务"
    
    local hpo_ids=""
    if [ -s "$hpo_file" ]; then
        hpo_ids=$(cat "$hpo_file" | tr '\n' ',' | sed 's/,$//')
    fi

    log_info "关联传参的 HPO 词条: ${hpo_ids:-无}"

    local response
    if [ -n "$hpo_ids" ]; then
        response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time $CURL_TIMEOUT -X POST "${PPI_URL}/score/clean-case/upload/async" \
            -F "phenotype_gene_csv=@${gene_phenotype_csv}" \
            -F "vep_output_csv=@${vep_csv}" \
            -F "hpo_ids=${hpo_ids}" 2>/dev/null)
    else
        response=$(curl -s --connect-timeout $CONNECT_TIMEOUT --max-time $CURL_TIMEOUT -X POST "${PPI_URL}/score/clean-case/upload/async" \
            -F "phenotype_gene_csv=@${gene_phenotype_csv}" \
            -F "vep_output_csv=@${vep_csv}" 2>/dev/null)
    fi

    log_info "PPI服务返回的原始响应: $response"

    local job_id
    job_id=$(json_get "$response" "job_id" "")
    
    if [ -z "$job_id" ]; then
        log_error "PPI任务提交失败: $response"
        return 1
    fi
    
    log_info "PPI任务ID: $job_id"
    
    wait_for_job "${PPI_URL}/score/${job_id}" "PPI" || return 1
    
    local ppi_csv="${output_dir}/final_score.csv"
    local current_dir=$(pwd)
    cd "$output_dir"
    curl -s --connect-timeout $CONNECT_TIMEOUT --max-time 300 -OJ "${PPI_URL}/score/${job_id}/csv" 2>/dev/null
    
    local downloaded_file=$(ls -t *.csv 2>/dev/null | grep -v "gene_phenotype\|variant_phenotype\|vep_output" | head -1)
    if [ -n "$downloaded_file" ] && [ -f "$downloaded_file" ]; then
        mv "$downloaded_file" "final_score.csv"
        log_success "PPI结果已保存: $ppi_csv"
    else
        log_warning "无法定位下载的PPI结果文件"
        ppi_csv=""
    fi
    cd "$current_dir"
    
    echo "$ppi_csv"
}

# Step 5: Rare Disease Report服务
run_report() {
    local wide_csv=$1
    local phenotype_csv=$2
    local ppi_csv=$3
    local hpo_file=$4
    local symptom_text=$5
    local output_dir=$6
    
    log_info "提交报告生成任务"
    
    local escaped_text=$(echo "$symptom_text" | $PYTHON -c "
import sys, json
print(json.dumps(sys.stdin.read().strip())[1:-1])
")
    
    local report_file="${output_dir}/report.md"
    local pdf_file="${output_dir}/report.pdf"
    > "$report_file"
    
    log_info "开始接收报告内容..."
    
    $PYTHON << PYEOF
import requests
import json
import sys

url = "${REPORT_URL}/report/stream"

data = {
    "wide": "${wide_csv}",
    "phenotype": "${phenotype_csv}" if "${phenotype_csv}" else None,
    "ppi": "${ppi_csv}" if "${ppi_csv}" else None,
    "hpo_file": "${hpo_file}",
    "symptom_text": "${escaped_text}",
    "top_n": 10,
    "k": 5
}

report_lines = []
run_id = ""
pdf_url = ""

try:
    response = requests.post(url, json=data, stream=True, timeout=600)
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith('data:'):
            try:
                d = json.loads(line[5:].strip())
                event_type = d.get('type', '')
                
                if event_type == 'meta':
                    run_id = d.get('run_id', '')
                    genes = d.get('genes', [])
                    print(f"[INFO] 报告任务ID: {run_id}")
                    print(f"[INFO] 候选基因: {', '.join(genes)}")
                    sys.stdout.flush()
                elif event_type == 'md':
                    text = d.get('text', '')
                    if text:
                        report_lines.append(text)
                elif event_type == 'done':
                    pdf_url = d.get('pdf_url', '')
                    if pdf_url:
                        print(f"[SUCCESS] PDF下载地址: {pdf_url}")
                        sys.stdout.flush()
            except json.JSONDecodeError:
                pass
except Exception as e:
    print(f"[ERROR] 报告生成失败: {e}", file=sys.stderr)
    sys.exit(1)

if report_lines:
    with open('$report_file', 'w') as f:
        f.write(''.join(report_lines))
    print(f"[SUCCESS] Markdown报告已保存: $report_file")
    sys.stdout.flush()

if pdf_url:
    import subprocess
    full_url = f'${REPORT_URL}{pdf_url}'
    subprocess.run(['curl', '-s', '-o', '$pdf_file', full_url], check=True)
    print(f"[SUCCESS] PDF报告已保存: $pdf_file")
    sys.stdout.flush()
PYEOF
}

# ==================== 主程序 ====================

# ==================== 主程序 (完美修复保底覆盖Bug) ====================

main() {
    local vcf_file=""
    local text_input=""
    local output_dir=""
    
    while getopts "v:t:o:h" opt; do
        case $opt in
            v) vcf_file="$OPTARG" ;;
            t) text_input="$OPTARG" ;;
            o) output_dir="$OPTARG" ;;
            *) usage ;;
        esac
    done
    
    if [ -z "$vcf_file" ] || [ -z "$text_input" ]; then log_error "必须提供VCF文件和描述文本"; usage; fi
    if [ ! -f "$vcf_file" ]; then log_error "VCF文件不存在: $vcf_file"; exit 1; fi
    if [ -z "$output_dir" ]; then output_dir="./rare_disease_output_$(date +%Y%m%d_%H%M%S)"; fi
    mkdir -p "$output_dir"
    
    log_info "========== 罕见病分析流程启动 =========="
    log_info "输出目录: $output_dir"
    log_info "输入VCF: $vcf_file"
    
    # 定义确定性的 HPO 文件路径，不再盲目信任函数的 stdout 字符串捕获
    local hpo_file="${output_dir}/hpo_terms.txt"
    
    # Step 1: HPO RAG
    log_info "Step 1/5: HPO词条提取"
    
    # 显式执行函数，让它把数据直接打入预定路径
    run_hpo_rag "$text_input" "$output_dir" >/dev/null
    
    # 健壮性检查：直接检查实体文件是否真的存在且有内容
    if [ -s "$hpo_file" ]; then
        log_success "主流程确认：HPO词条文件安全就绪，共计 $(wc -l < "$hpo_file") 条症状词"
    else
        log_warning "主流程警告：HPO RAG 未能产生有效词条，将使用空 HPO 文件维持下游流程"
        touch "$hpo_file"
    fi
    

    # Step 1.5: VCF Liftover（如果需要）
    # 这里我们假设输入的 VCF 可能是 GRCh37，如果是 GRCh38 就直接跳过 liftover 步骤，继续后续流程
    log_info "Step 1.5/5: VCF Liftover（如果需要）"
    local liftover_vcf=""
    if check_service "${LIFTOVER_URL}/health"; then
        log_info "检测到 Liftover 服务可用，准备进行坐标转换（如果输入VCF已是GRCh38则会自动跳过转换）..."
        liftover_vcf=$(run_liftover "$vcf_file" "$output_dir" "sample_liftover")
        if [ -n "$liftover_vcf" ]; then
            log_success "Liftover 处理完成，后续流程将使用转换后的 VCF 文件: $liftover_vcf"
            vcf_file="$liftover_vcf"
        else
            log_warning "Liftover 处理失败或被跳过，将继续使用原始 VCF 文件: $vcf_file"
        fi
    else
        log_warning "未检测到 Liftover 服务，跳过坐标转换步骤，将继续使用原始 VCF 文件: $vcf_file"
    fi
    
    local vcf_to_use="$vcf_file"
    if [ -n "$liftover_vcf" ]; then
        vcf_to_use="$liftover_vcf"
    fi


    # Step 2: VEP
    log_info "Step 2/5: VEP注释（含组织特异性）"
    local vep_csv="${output_dir}/vep_output.csv"
    run_vep "$vcf_to_use" "$hpo_file" "$output_dir"
    if [ -z "$vep_csv" ] || [ ! -f "$vep_csv" ]; then log_error "VEP服务处理异常终止"; exit 1; fi
    
    # Step 3: 表型-HPO评分
    log_info "Step 3/5: 表型-HPO评分"
    # local phenotype_result
    phenotype_result=$(run_phenotype_score "$vep_csv" "$hpo_file" "$output_dir")
    local gene_phenotype_csv=$(echo "$phenotype_result" | cut -d'|' -f1)
    local variant_phenotype_csv=$(echo "$phenotype_result" | cut -d'|' -f2)
    local gene_phenotype_csv="${output_dir}/gene_phenotype_score.csv"
    local variant_phenotype_csv="${output_dir}/variant_phenotype_score.csv"

    # Step 4: PPI
    log_info "Step 4/5: PPI网络分析"
    local ppi_csv=""
    ppi_csv=$(run_ppi "$gene_phenotype_csv" "$vep_csv" "$hpo_file" "$output_dir") || log_warning "PPI网络分析不可用，跳过"
    
    # Step 5: Report
    log_info "Step 5/5: 生成报告"
    run_report "$vep_csv" "$gene_phenotype_csv" "$ppi_csv" "$hpo_file" "$text_input" "$output_dir"
    
    log_success "========== 罕见病分析流程执行完成 =========="
}

main "$@"