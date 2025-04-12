import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { AnalyticsDashboard } from './Dashboard';
import { useAnalyticsStore } from '@/stores/analytics';

// Mock the analytics store
vi.mock('@/stores/analytics', () => ({
  useAnalyticsStore: vi.fn(),
}));

describe('AnalyticsDashboard', () => {
  const mockAnalyticsData = {
    stats: {
      totalDocuments: 10,
      documentsChange: 5,
      totalReadingTime: 120,
      readingTimeChange: 10,
      averageSpeed: 200,
      speedChange: 15,
      completionRate: 75,
      completionChange: 5,
      peakTime: '14:00 - 16:00',
      avgSession: 30,
      documentsPerDay: 2,
      wordsPerDay: 1000,
    },
    topDocuments: [
      {
        id: '1',
        title: 'Test Document 1',
        type: 'PDF',
        readingTime: 60,
        completion: 100,
        speed: 250,
      },
    ],
    activityData: {
      labels: ['2023-01-01', '2023-01-02'],
      values: [30, 45],
    },
    typesData: {
      labels: ['PDF', 'EPUB'],
      values: [8, 2],
    },
    speedData: {
      labels: ['2023-01-01', '2023-01-02'],
      values: [200, 220],
    },
    completionData: {
      labels: ['2023-01-01', '2023-01-02'],
      values: [70, 80],
    },
  };

  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();

    // Setup store mock
    (useAnalyticsStore as any).mockReturnValue({
      getAnalytics: vi.fn().mockResolvedValue(mockAnalyticsData),
      exportData: vi.fn().mockResolvedValue(undefined),
      loading: false,
      error: null,
    });
  });

  it('renders the dashboard header', () => {
    render(<AnalyticsDashboard />);
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
  });

  it('displays summary cards with correct data', async () => {
    render(<AnalyticsDashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('10')).toBeInTheDocument(); // Total Documents
      expect(screen.getByText('2h 0m')).toBeInTheDocument(); // Reading Time
      expect(screen.getByText('200 wpm')).toBeInTheDocument(); // Reading Speed
      expect(screen.getByText('75%')).toBeInTheDocument(); // Completion Rate
    });
  });

  it('handles date range changes', async () => {
    render(<AnalyticsDashboard />);
    
    const dateRangeSelect = screen.getByLabelText('Date Range:');
    fireEvent.change(dateRangeSelect, { target: { value: '7' } });

    await waitFor(() => {
      expect(useAnalyticsStore().getAnalytics).toHaveBeenCalledWith('7');
    });
  });

  it('handles export data', async () => {
    render(<AnalyticsDashboard />);
    
    const exportButton = screen.getByText('Export Data');
    fireEvent.click(exportButton);

    await waitFor(() => {
      expect(useAnalyticsStore().exportData).toHaveBeenCalled();
    });
  });

  it('displays loading state', () => {
    (useAnalyticsStore as any).mockReturnValue({
      ...useAnalyticsStore(),
      loading: true,
    });

    render(<AnalyticsDashboard />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('displays error state', () => {
    (useAnalyticsStore as any).mockReturnValue({
      ...useAnalyticsStore(),
      error: 'Failed to fetch analytics',
    });

    render(<AnalyticsDashboard />);
    expect(screen.getByText('Failed to fetch analytics')).toBeInTheDocument();
  });
}); 