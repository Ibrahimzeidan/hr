/**
 * Tests for Export Buttons functionality
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

// Mock API service
const mockExportCSV = vi.fn();
const mockExportExcel = vi.fn();

// Export Buttons component
function ExportButtons({
  onExportCSV,
  onExportExcel,
  disabled = false,
}: {
  onExportCSV: () => void;
  onExportExcel: () => void;
  disabled?: boolean;
}) {
  return (
    <div data-testid="export-buttons">
      <button
        onClick={onExportCSV}
        disabled={disabled}
        data-testid="export-csv-btn"
      >
        Export CSV
      </button>
      <button
        onClick={onExportExcel}
        disabled={disabled}
        data-testid="export-excel-btn"
      >
        Export Excel
      </button>
    </div>
  );
}

describe('ExportButtons', () => {
  it('renders both export buttons', () => {
    render(
      <ExportButtons onExportCSV={() => {}} onExportExcel={() => {}} />
    );

    expect(screen.getByTestId('export-csv-btn')).toBeInTheDocument();
    expect(screen.getByTestId('export-excel-btn')).toBeInTheDocument();
  });

  it('calls onExportCSV when CSV button is clicked', () => {
    const onExportCSV = vi.fn();
    render(
      <ExportButtons onExportCSV={onExportCSV} onExportExcel={() => {}} />
    );

    fireEvent.click(screen.getByTestId('export-csv-btn'));

    expect(onExportCSV).toHaveBeenCalledTimes(1);
  });

  it('calls onExportExcel when Excel button is clicked', () => {
    const onExportExcel = vi.fn();
    render(
      <ExportButtons onExportCSV={() => {}} onExportExcel={onExportExcel} />
    );

    fireEvent.click(screen.getByTestId('export-excel-btn'));

    expect(onExportExcel).toHaveBeenCalledTimes(1);
  });

  it('disables buttons when disabled prop is true', () => {
    render(
      <ExportButtons
        onExportCSV={() => {}}
        onExportExcel={() => {}}
        disabled={true}
      />
    );

    expect(screen.getByTestId('export-csv-btn')).toBeDisabled();
    expect(screen.getByTestId('export-excel-btn')).toBeDisabled();
  });

  it('enables buttons when disabled prop is false', () => {
    render(
      <ExportButtons
        onExportCSV={() => {}}
        onExportExcel={() => {}}
        disabled={false}
      />
    );

    expect(screen.getByTestId('export-csv-btn')).not.toBeDisabled();
    expect(screen.getByTestId('export-excel-btn')).not.toBeDisabled();
  });

  it('shows loading state during export', () => {
    const ExportWithLoading = ({ loading }: { loading: boolean }) => (
      <div>
        <ExportButtons onExportCSV={() => {}} onExportExcel={() => {}} disabled={loading} />
        {loading && <span data-testid="loading-indicator">Exporting...</span>}
      </div>
    );

    const { rerender } = render(<ExportWithLoading loading={false} />);
    expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();

    rerender(<ExportWithLoading loading={true} />);
    expect(screen.getByTestId('loading-indicator')).toHaveTextContent('Exporting...');
    expect(screen.getByTestId('export-csv-btn')).toBeDisabled();
  });
});