/**
 * Tests for Search and Filter functionality
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';

// Sample candidate type
type Candidate = {
  id: number;
  full_name: string;
  email: string | null;
  score: number;
  rank: number | null;
  analysis: {
    matching_skills: string[];
    hiring_recommendation?: string;
  } | null;
};

// Search Input component
function SearchInput({
  value,
  onChange,
  placeholder = 'Search...',
}: {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      data-testid="search-input"
    />
  );
}

// Filter Select component
function FilterSelect({
  value,
  onChange,
  options,
  label,
}: {
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
  label: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      data-testid="filter-select"
      aria-label={label}
    >
      <option value="">All</option>
      {options.map((opt) => (
        <option key={opt.value} value={opt.value}>
          {opt.label}
        </option>
      ))}
    </select>
  );
}

// Candidate list with search and filter
function CandidateList({
  candidates,
  search,
  filterRecommendation,
}: {
  candidates: Candidate[];
  search: string;
  filterRecommendation: string;
}) {
  const filtered = candidates.filter((c) => {
    const matchesSearch =
      !search ||
      c.full_name.toLowerCase().includes(search.toLowerCase()) ||
      c.email?.toLowerCase().includes(search.toLowerCase());

    const matchesFilter =
      !filterRecommendation ||
      c.analysis?.hiring_recommendation === filterRecommendation;

    return matchesSearch && matchesFilter;
  });

  return (
    <ul data-testid="candidate-list">
      {filtered.map((c) => (
        <li key={c.id} data-testid={`candidate-${c.id}`}>
          {c.full_name} - {c.analysis?.hiring_recommendation || 'N/A'}
        </li>
      ))}
    </ul>
  );
}

describe('Search and Filter', () => {
  const mockCandidates: Candidate[] = [
    {
      id: 1,
      full_name: 'Alice Johnson',
      email: 'alice@example.com',
      score: 85,
      rank: 1,
      analysis: {
        matching_skills: ['Python'],
        hiring_recommendation: 'Hire',
      },
    },
    {
      id: 2,
      full_name: 'Bob Smith',
      email: 'bob@example.com',
      score: 92,
      rank: 2,
      analysis: {
        matching_skills: ['Java'],
        hiring_recommendation: 'Strong Hire',
      },
    },
    {
      id: 3,
      full_name: 'Charlie Brown',
      email: 'charlie@example.com',
      score: 60,
      rank: 3,
      analysis: {
        matching_skills: ['JavaScript'],
        hiring_recommendation: 'Consider',
      },
    },
  ];

  describe('SearchInput', () => {
    it('renders with placeholder', () => {
      render(<SearchInput value="" onChange={() => {}} placeholder="Search candidates..." />);
      expect(screen.getByTestId('search-input')).toHaveAttribute(
        'placeholder',
        'Search candidates...'
      );
    });

    it('displays current value', () => {
      render(<SearchInput value="Alice" onChange={() => {}} />);
      expect(screen.getByTestId('search-input')).toHaveValue('Alice');
    });

    it('calls onChange when typing', () => {
      const onChange = vi.fn();
      render(<SearchInput value="" onChange={onChange} />);

      fireEvent.change(screen.getByTestId('search-input'), {
        target: { value: 'test' },
      });

      expect(onChange).toHaveBeenCalledWith('test');
    });
  });

  describe('FilterSelect', () => {
    const options = [
      { value: 'Strong Hire', label: 'Strong Hire' },
      { value: 'Hire', label: 'Hire' },
      { value: 'Consider', label: 'Consider' },
    ];

    it('renders with options', () => {
      render(
        <FilterSelect
          value=""
          onChange={() => {}}
          options={options}
          label="Recommendation"
        />
      );

      expect(screen.getByTestId('filter-select')).toBeInTheDocument();
      expect(screen.getByText('Strong Hire')).toBeInTheDocument();
      expect(screen.getByText('Hire')).toBeInTheDocument();
      expect(screen.getByText('Consider')).toBeInTheDocument();
    });

    it('shows selected value', () => {
      render(
        <FilterSelect
          value="Hire"
          onChange={() => {}}
          options={options}
          label="Recommendation"
        />
      );

      expect(screen.getByTestId('filter-select')).toHaveValue('Hire');
    });

    it('calls onChange when selection changes', () => {
      const onChange = vi.fn();
      render(
        <FilterSelect
          value=""
          onChange={onChange}
          options={options}
          label="Recommendation"
        />
      );

      fireEvent.change(screen.getByTestId('filter-select'), {
        target: { value: 'Hire' },
      });

      expect(onChange).toHaveBeenCalledWith('Hire');
    });
  });

  describe('CandidateList Filtering', () => {
    it('filters by search term', () => {
      const { rerender } = render(
        <CandidateList candidates={mockCandidates} search="" filterRecommendation="" />
      );
      expect(screen.getAllByTestId(/candidate-/)).toHaveLength(3);

      rerender(
        <CandidateList candidates={mockCandidates} search="Alice" filterRecommendation="" />
      );
      expect(screen.getByTestId('candidate-1')).toBeInTheDocument();
      expect(screen.queryByTestId('candidate-2')).not.toBeInTheDocument();
    });

    it('filters by recommendation', () => {
      const { rerender } = render(
        <CandidateList candidates={mockCandidates} search="" filterRecommendation="" />
      );

      rerender(
        <CandidateList
          candidates={mockCandidates}
          search=""
          filterRecommendation="Hire"
        />
      );
      expect(screen.getByTestId('candidate-1')).toBeInTheDocument();
      expect(screen.queryByTestId('candidate-2')).not.toBeInTheDocument();
    });

    it('combines search and filter', () => {
      const { rerender } = render(
        <CandidateList candidates={mockCandidates} search="" filterRecommendation="" />
      );

      rerender(
        <CandidateList
          candidates={mockCandidates}
          search="Smith"
          filterRecommendation="Strong Hire"
        />
      );
      expect(screen.getByTestId('candidate-2')).toBeInTheDocument();
      expect(screen.queryByTestId('candidate-1')).not.toBeInTheDocument();
    });

    it('shows all when no filters applied', () => {
      render(
        <CandidateList candidates={mockCandidates} search="" filterRecommendation="" />
      );
      expect(screen.getAllByTestId(/candidate-/)).toHaveLength(3);
    });
  });
});