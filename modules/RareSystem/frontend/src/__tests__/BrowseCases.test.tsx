/**
 * Tests for BrowseCases delete functionality - TDD Red Phase.
 * These tests are expected to FAIL until the delete UI is implemented.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import BrowseCases from '../pages/BrowseCases'

// Mock the API module
vi.mock('../services/api', () => ({
  default: {
    getCases: vi.fn(),
    deleteCase: vi.fn(),
  },
}))

import api from '../services/api'

// vi.mock is hoisted above every other statement in this file, so anything it
// references must be hoisted too -- a plain `const` declared next to the mock
// (or worse, inside a test body) is still in the temporal dead zone when the
// factory runs, and the whole module fails to load.
const { mockMessageError } = vi.hoisted(() => ({ mockMessageError: vi.fn() }))

vi.mock('antd', async () => {
  const actual = await vi.importActual<typeof import('antd')>('antd')
  return {
    ...actual,
    message: {
      ...actual.message,
      error: mockMessageError,
    },
  }
})

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Wrapper for rendering with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

// Sample test data
const mockCases = [
  {
    patient_id: 1,
    patient_name: 'Patient 1',
    age: 30,
    sex: 'M',
    ethnicity: 'Asian',
    diagnosis_description: 'Test diagnosis 1',
    medical_history: 'Test history 1',
    vcf_files: [
      { id: 1, file_name: 'test1.vcf', upload_date: '2024-01-01', variant_count: 100, classified_count: 10 }
    ],
    total_variants: 100,
    total_classified: 10,
  },
  {
    patient_id: 2,
    patient_name: 'Patient 2',
    age: 25,
    sex: 'F',
    ethnicity: 'Caucasian',
    diagnosis_description: 'Test diagnosis 2',
    medical_history: 'Test history 2',
    vcf_files: [
      { id: 2, file_name: 'test2.vcf', upload_date: '2024-01-02', variant_count: 200, classified_count: 20 }
    ],
    total_variants: 200,
    total_classified: 20,
  },
]

describe('BrowseCases Delete Functionality', () => {
  const mockOnOpenCase = vi.fn()
  const mockOnDeleteCase = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    ;(api.getCases as ReturnType<typeof vi.fn>).mockResolvedValue({
      cases: mockCases,
      total: mockCases.length,
    })
  })

  describe('Delete Button Rendering', () => {
    it('renders delete button for each case row', async () => {
      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })
    })

    it('renders delete button in Action column alongside Open button', async () => {
      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        const openButtons = screen.getAllByRole('button', { name: /open/i })
        const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
        expect(openButtons).toHaveLength(2)
        expect(deleteButtons).toHaveLength(2)
      })
    })
  })

  describe('Delete Confirmation (Popconfirm)', () => {
    it('shows Popconfirm on delete button click', async () => {
      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      // Click the first delete button
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      fireEvent.click(deleteButtons[0])

      // Popconfirm should appear with confirmation text
      await waitFor(() => {
        expect(screen.getByText(/are you sure/i)).toBeInTheDocument()
      })
    })

    it('shows warning text in Popconfirm', async () => {
      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      fireEvent.click(deleteButtons[0])

      await waitFor(() => {
        expect(screen.getByText(/cannot be undone/i)).toBeInTheDocument()
      })
    })
  })

  describe('Active Case Protection', () => {
    it('disables delete button for active case', async () => {
      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={1}  // Patient 1 is active
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      
      // First delete button (Patient 1) should be disabled
      expect(deleteButtons[0]).toBeDisabled()
      
      // Second delete button (Patient 2) should NOT be disabled
      expect(deleteButtons[1]).not.toBeDisabled()
    })

    it('shows tooltip when hovering disabled delete button', async () => {
      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={1}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      
      // Hover over disabled button
      fireEvent.mouseEnter(deleteButtons[0])

      await waitFor(() => {
        expect(screen.getByText(/currently open/i)).toBeInTheDocument()
      })
    })
  })

  describe('Delete Action', () => {
    it('calls onDeleteCase when Popconfirm is confirmed', async () => {
      ;(api.deleteCase as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        message: 'Case deleted',
        patient_id: 1,
      })

      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      // Click delete button
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      fireEvent.click(deleteButtons[0])

      // Click confirm in Popconfirm
      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /ok|confirm|yes/i })
        fireEvent.click(confirmButton)
      })

      // Verify API was called
      await waitFor(() => {
        expect(api.deleteCase).toHaveBeenCalledWith(1)
      })

      // Verify onDeleteCase callback was called
      await waitFor(() => {
        expect(mockOnDeleteCase).toHaveBeenCalledWith(1)
      })
    })

    it('does not call onDeleteCase when Popconfirm is cancelled', async () => {
      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      // Click delete button
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      fireEvent.click(deleteButtons[0])

      // Click cancel in Popconfirm
      await waitFor(() => {
        const cancelButton = screen.getByRole('button', { name: /cancel|no/i })
        fireEvent.click(cancelButton)
      })

      // Verify API was NOT called
      expect(api.deleteCase).not.toHaveBeenCalled()
      expect(mockOnDeleteCase).not.toHaveBeenCalled()
    })
  })

  describe('Loading State', () => {
    it('shows loading spinner on delete button during API call', async () => {
      // Create a promise that we can resolve manually
      let resolveDelete: (value: unknown) => void
      const deletePromise = new Promise((resolve) => {
        resolveDelete = resolve
      })
      ;(api.deleteCase as ReturnType<typeof vi.fn>).mockReturnValueOnce(deletePromise)

      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      // Click delete button
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      fireEvent.click(deleteButtons[0])

      // Click confirm
      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /ok|confirm|yes/i })
        fireEvent.click(confirmButton)
      })

      // Check for loading state (spinner or loading prop)
      await waitFor(() => {
        const deleteButton = deleteButtons[0]
        expect(deleteButton).toHaveAttribute('loading') // Ant Design loading prop
      })

      // Resolve the promise
      resolveDelete!({ message: 'Case deleted', patient_id: 1 })

      // Wait for loading to finish
      await waitFor(() => {
        expect(mockOnDeleteCase).toHaveBeenCalled()
      })
    })
  })

  describe('Error Handling', () => {
    it('shows error message when delete fails', async () => {
      ;(api.deleteCase as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
        new Error('Failed to delete case')
      )

      renderWithRouter(
        <BrowseCases 
          onOpenCase={mockOnOpenCase}
          activePatientId={null}
          onDeleteCase={mockOnDeleteCase}
        />
      )

      await waitFor(() => {
        expect(screen.getAllByRole('button', { name: /delete/i })).toHaveLength(2)
      })

      // Click delete button
      const deleteButtons = screen.getAllByRole('button', { name: /delete/i })
      fireEvent.click(deleteButtons[0])

      // Click confirm
      await waitFor(() => {
        const confirmButton = screen.getByRole('button', { name: /ok|confirm|yes/i })
        fireEvent.click(confirmButton)
      })

      // Verify error message was shown
      await waitFor(() => {
        expect(mockMessageError).toHaveBeenCalled()
      })

      // Verify onDeleteCase was NOT called
      expect(mockOnDeleteCase).not.toHaveBeenCalled()
    })
  })
})
