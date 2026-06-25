import React, { useRef, useEffect } from 'react'
import { Card, Space, Typography, Empty, Row, Col } from 'antd'
import { BarChartOutlined, PieChartOutlined } from '@ant-design/icons'
import { Chart } from '@antv/g2'
import type { Variant, ACMGClassification } from '@/types'

const { Text } = Typography

interface VariantVisualizationProps {
  variants: Variant[]
  classifications: ACMGClassification[]
}

const VariantVisualization: React.FC<VariantVisualizationProps> = ({ variants, classifications }) => {
  const chromosomeChartRef = useRef<HTMLDivElement>(null)
  const classificationChartRef = useRef<HTMLDivElement>(null)
  const typeChartRef = useRef<HTMLDivElement>(null)
  const afDistributionRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!variants.length) return

    if (chromosomeChartRef.current) {
      const chromosomeData = variants.reduce((acc, v) => {
        const chr = v.chromosome.replace('chr', '')
        acc[chr] = (acc[chr] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      const chartData = Object.entries(chromosomeData)
        .map(([chromosome, count]) => ({ chromosome, count }))
        .sort((a, b) => {
          const aNum = parseInt(a.chromosome) || (a.chromosome === 'X' ? 23 : a.chromosome === 'Y' ? 24 : 25)
          const bNum = parseInt(b.chromosome) || (b.chromosome === 'X' ? 23 : b.chromosome === 'Y' ? 24 : 25)
          return aNum - bNum
        })

      const chart = new Chart({
        container: chromosomeChartRef.current,
        autoFit: true,
        height: 250,
      })

      chart
        .interval()
        .data(chartData)
        .encode('x', 'chromosome')
        .encode('y', 'count')
        .encode('color', 'chromosome')
        .axis('x', { title: 'Chromosome' })
        .axis('y', { title: 'Variant Count' })
        .style('fillOpacity', 0.8)

      chart.render()

      return () => chart.destroy()
    }
  }, [variants])

  useEffect(() => {
    if (!classifications.length) return

    if (classificationChartRef.current) {
      const classificationData = classifications.reduce((acc, c) => {
        acc[c.classification] = (acc[c.classification] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      const chartData = Object.entries(classificationData).map(([classification, value]) => ({
        classification,
        value,
      }))

      const chart = new Chart({
        container: classificationChartRef.current,
        autoFit: true,
        height: 250,
      })

      chart
        .interval()
        .data(chartData)
        .encode('x', 'classification')
        .encode('y', 'value')
        .encode('color', 'classification')
        .axis('x', { title: null, labelAutoRotate: true })
        .axis('y', { title: 'Count' })
        .style('fillOpacity', 0.85)

      chart.render()

      return () => chart.destroy()
    }
  }, [classifications])

  useEffect(() => {
    if (!variants.length) return

    if (typeChartRef.current) {
      const typeData = variants.reduce((acc, v) => {
        acc[v.variant_type] = (acc[v.variant_type] || 0) + 1
        return acc
      }, {} as Record<string, number>)

      const chartData = Object.entries(typeData).map(([type, value]) => ({ type, value }))

      const chart = new Chart({
        container: typeChartRef.current,
        autoFit: true,
        height: 250,
      })

      chart
        .interval()
        .data(chartData)
        .encode('x', 'type')
        .encode('y', 'value')
        .encode('color', 'type')
        .axis('x', { title: 'Variant Type' })
        .axis('y', { title: 'Count' })
        .style('fillOpacity', 0.8)

      chart.render()

      return () => chart.destroy()
    }
  }, [variants])

  useEffect(() => {
    if (!variants.length) return

    if (afDistributionRef.current) {
      const afData = variants
        .filter((v) => v.gnomad_af !== undefined && v.gnomad_af !== null)
        .map((v) => ({
          af: Math.log10(v.gnomad_af! + 1e-10),
          afLabel: v.gnomad_af! === 0 ? '0' : v.gnomad_af! < 0.0001 ? '<0.01%' : v.gnomad_af! < 0.01 ? '<1%' : '>1%',
        }))

      const chart = new Chart({
        container: afDistributionRef.current,
        autoFit: true,
        height: 250,
      })

      chart
        .interval()
        .data(afData)
        .encode('x', 'af')
        .encode('y', 'count')
        .axis('x', { title: 'gnomAD AF (log10)', labelAutoRotate: true })
        .axis('y', { title: 'Variant Count' })

      chart.render()

      return () => chart.destroy()
    }
  }, [variants])

  if (!variants.length) {
    return (
      <Empty description="No variant data to visualize">
        <Text type="secondary">Upload a VCF file to see visualizations</Text>
      </Empty>
    )
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card
            title={
              <Space>
                <BarChartOutlined />
                <span>Variants by Chromosome</span>
              </Space>
            }
            size="small"
          >
            <div ref={chromosomeChartRef} />
          </Card>
        </Col>
        <Col span={12}>
          <Card
            title={
              <Space>
                <PieChartOutlined />
                <span>Classification Distribution</span>
              </Space>
            }
            size="small"
          >
            <div ref={classificationChartRef} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card
            title={
              <Space>
                <BarChartOutlined />
                <span>Variant Types</span>
              </Space>
            }
            size="small"
          >
            <div ref={typeChartRef} />
          </Card>
        </Col>
        <Col span={12}>
          <Card
            title={
              <Space>
                <BarChartOutlined />
                <span>Allele Frequency Distribution</span>
              </Space>
            }
            size="small"
          >
            <div ref={afDistributionRef} />
          </Card>
        </Col>
      </Row>
    </Space>
  )
}

export default VariantVisualization
