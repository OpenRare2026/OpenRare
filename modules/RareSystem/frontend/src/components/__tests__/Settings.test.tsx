import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import Settings from '@/components/Settings'

vi.mock('@/services/api', () => ({
  default: {
    getProviders: vi.fn(() => Promise.resolve([
      { code: 'openai', name: 'OpenAI', models: ['gpt-4o-mini', 'gpt-4o'] },
      { code: 'anthropic', name: 'Anthropic', models: ['claude-3-haiku-20240307'] },
      { code: 'ollama', name: 'Ollama (本地)', models: ['llama3', 'mistral'] },
    ])),
    getLLMSettings: vi.fn(() => Promise.reject({ status: 404 })),
    saveLLMSettings: vi.fn(() => Promise.resolve({ id: 1, provider: 'openai', model: 'gpt-4o-mini' })),
  },
}))

describe('Settings Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders settings form', async () => {
    render(<Settings />)
    
    await waitFor(() => {
      // "LLM Settings" appears twice: as the tab label and as the card
      // heading. Query the heading so the assertion stays unambiguous.
      expect(screen.getByRole('heading', { name: 'LLM Settings' })).toBeInTheDocument()
    })
  })

  it('shows provider select', async () => {
    render(<Settings />)
    
    await waitFor(() => {
      expect(screen.getByLabelText('LLM Provider')).toBeInTheDocument()
    })
  })

  it('shows API key input', async () => {
    render(<Settings />)
    
    await waitFor(() => {
      expect(screen.getByLabelText('API Key')).toBeInTheDocument()
    })
  })

  it('shows model select', async () => {
    render(<Settings />)
    
    await waitFor(() => {
      expect(screen.getByLabelText('Model')).toBeInTheDocument()
    })
  })

  it('shows save button', async () => {
    render(<Settings />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /save settings/i })).toBeInTheDocument()
    })
  })

  it('shows reset button', async () => {
    render(<Settings />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /reset/i })).toBeInTheDocument()
    })
  })

  it('shows info alert', async () => {
    render(<Settings />)
    
    await waitFor(() => {
      expect(screen.getByText(/Configure Large Language Model/i)).toBeInTheDocument()
    })
  })
})
