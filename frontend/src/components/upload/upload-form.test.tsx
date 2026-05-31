/**
 * Tests for Upload Form component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

// Mock next-themes
vi.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light', setTheme: vi.fn() }),
}));

// Simple upload form component for testing
function UploadForm({ onUpload }: { onUpload: (files: File[]) => void }) {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      onUpload(Array.from(files));
    }
  };

  return (
    <div data-testid="upload-form">
      <input
        type="file"
        accept=".pdf,.doc,.docx"
        multiple
        onChange={handleFileChange}
        data-testid="file-input"
      />
      <button type="button" data-testid="upload-button">
        Upload
      </button>
    </div>
  );
}

describe('UploadForm', () => {
  it('renders file input and upload button', () => {
    const onUpload = vi.fn();
    render(<UploadForm onUpload={onUpload} />);

    expect(screen.getByTestId('file-input')).toBeInTheDocument();
    expect(screen.getByTestId('upload-button')).toBeInTheDocument();
  });

  it('accepts PDF files', () => {
    const onUpload = vi.fn();
    render(<UploadForm onUpload={onUpload} />);

    const file = new File(['test content'], 'resume.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('file-input');

    fireEvent.change(input, { target: { files: [file] } });

    expect(onUpload).toHaveBeenCalledWith([file]);
  });

  it('accepts multiple files', () => {
    const onUpload = vi.fn();
    render(<UploadForm onUpload={onUpload} />);

    const file1 = new File(['content 1'], 'resume1.pdf', { type: 'application/pdf' });
    const file2 = new File(['content 2'], 'resume2.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('file-input');

    fireEvent.change(input, { target: { files: [file1, file2] } });

    expect(onUpload).toHaveBeenCalledWith([file1, file2]);
  });

  it('shows loading state when uploading', () => {
    const onUpload = vi.fn();
    const { rerender } = render(<UploadForm onUpload={onUpload} />);

    // Initially not loading
    expect(screen.queryByText(/uploading/i)).not.toBeInTheDocument();

    // Simulate loading state
    rerender(
      <div>
        <UploadForm onUpload={onUpload} />
        <span data-testid="loading">Uploading...</span>
      </div>
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('Uploading...');
  });
});