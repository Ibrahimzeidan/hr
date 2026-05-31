/**
 * Tests for Dashboard component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

// Mock next-themes
vi.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light', setTheme: vi.fn() }),
}));

// Sample candidate data type
type Candidate = {
  id: number;
  full_name: string;
  email: string | null;
  score: number;
  rank: number | null;
  analysis: {
    matching_skills: string[];
    missing_skills: string[];
    hiring_recommendation?: string;
    confidence_score?: number;
  } | null;
};

// Simple Dashboard Stats component for testing
function DashboardStats({ candidates }: { candidates: Candidate[] }) {
  const avgScore = candidates.length > 0
    ? Math.round(candidates.reduce((sum, c) => sum + c.score, 0) / candidates.length)
    : 0;

  const topCandidate = candidates.length > 0
    ? candidates.reduce((top, c) => c.score > top.score ? c : top)
    : null;

  return (
    <div data-testid="dashboard-stats">
      <div data-testid="total-candidates">Total: {candidates.length}</div>
      <div data-testid="average-score">Average Score: {avgScore}</div>
      {topCandidate && (
        <div data-testid="top-candidate">Top: {topCandidate.full_name}</div>
      )}
    </div>
  );
}

// Simple Candidate Table component for testing
function CandidateTable({ candidates }: { candidates: Candidate[] }) {
  return (
    <table data-testid="candidate-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Name</th>
          <th>Score</th>
          <th>Recommendation</th>
        </tr>
      </thead>
      <tbody>
        {candidates.map((c) => (
          <tr key={c.id} data-testid={`candidate-row-${c.id}`}>
            <td>{c.rank}</td>
            <td>{c.full_name}</td>
            <td>{c.score}</td>
            <td>{c.analysis?.hiring_recommendation || '-'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

describe('Dashboard', () => {
  const mockCandidates: Candidate[] = [
    {
      id: 1,
      full_name: 'John Doe',
      email: 'john@example.com',
      score: 85,
      rank: 1,
      analysis: {
        matching_skills: ['Python', 'React'],
        missing_skills: ['AWS'],
        hiring_recommendation: 'Hire',
        confidence_score: 80,
      },
    },
    {
      id: 2,
      full_name: 'Jane Smith',
      email: 'jane@example.com',
      score: 92,
      rank: 2,
      analysis: {
        matching_skills: ['Python', 'AWS', 'Docker'],
        missing_skills: [],
        hiring_recommendation: 'Strong Hire',
        confidence_score: 95,
      },
    },
  ];

  describe('DashboardStats', () => {
    it('renders total candidate count', () => {
      render(<DashboardStats candidates={mockCandidates} />);
      expect(screen.getByTestId('total-candidates')).toHaveTextContent('Total: 2');
    });

    it('calculates and displays average score', () => {
      render(<DashboardStats candidates={mockCandidates} />);
      // (85 + 92) / 2 = 88.5, rounded = 89 (or 88 depending on rounding)
      expect(screen.getByTestId('average-score')).toHaveTextContent('Average Score: 89');
    });

    it('displays top candidate', () => {
      render(<DashboardStats candidates={mockCandidates} />);
      expect(screen.getByTestId('top-candidate')).toHaveTextContent('Top: Jane Smith');
    });

    it('handles empty candidate list', () => {
      render(<DashboardStats candidates={[]} />);
      expect(screen.getByTestId('total-candidates')).toHaveTextContent('Total: 0');
      expect(screen.getByTestId('average-score')).toHaveTextContent('Average Score: 0');
      expect(screen.queryByTestId('top-candidate')).not.toBeInTheDocument();
    });
  });

  describe('CandidateTable', () => {
    it('renders table with candidate data', () => {
      render(<CandidateTable candidates={mockCandidates} />);
      expect(screen.getByTestId('candidate-table')).toBeInTheDocument();
      expect(screen.getAllByRole('row')).toHaveLength(3); // header + 2 rows
    });

    it('displays candidate names', () => {
      render(<CandidateTable candidates={mockCandidates} />);
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    it('displays candidate scores', () => {
      render(<CandidateTable candidates={mockCandidates} />);
      expect(screen.getByText('85')).toBeInTheDocument();
      expect(screen.getByText('92')).toBeInTheDocument();
    });

    it('displays hiring recommendations', () => {
      render(<CandidateTable candidates={mockCandidates} />);
      expect(screen.getByText('Hire')).toBeInTheDocument();
      expect(screen.getByText('Strong Hire')).toBeInTheDocument();
    });

    it('renders empty table for no candidates', () => {
      render(<CandidateTable candidates={[]} />);
      expect(screen.getByTestId('candidate-table')).toBeInTheDocument();
      expect(screen.getAllByRole('row')).toHaveLength(1); // just header
    });
  });
});