<template>
  <div class="analytics-dashboard">
    <div class="dashboard-header">
      <h1>Analytics Dashboard</h1>
      <div class="dashboard-actions">
        <div class="date-range">
          <label>Date Range:</label>
          <select v-model="dateRange" class="filter-select">
            <option value="7">Last 7 Days</option>
            <option value="30">Last 30 Days</option>
            <option value="90">Last 90 Days</option>
            <option value="365">Last Year</option>
          </select>
        </div>
        <button @click="exportData" class="btn btn-outline">
          <i class="fas fa-download"></i> Export Data
        </button>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- Summary Cards -->
      <div class="summary-grid">
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-book"></i>
          </div>
          <div class="card-content">
            <h3>Total Documents</h3>
            <p class="card-value">{{ stats.totalDocuments }}</p>
            <p class="card-change" :class="stats.documentsChange >= 0 ? 'positive' : 'negative'">
              <i :class="stats.documentsChange >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(stats.documentsChange) }}%
            </p>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>Reading Time</h3>
            <p class="card-value">{{ formatDuration(stats.totalReadingTime) }}</p>
            <p class="card-change" :class="stats.readingTimeChange >= 0 ? 'positive' : 'negative'">
              <i :class="stats.readingTimeChange >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(stats.readingTimeChange) }}%
            </p>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="card-content">
            <h3>Reading Speed</h3>
            <p class="card-value">{{ stats.averageSpeed }} wpm</p>
            <p class="card-change" :class="stats.speedChange >= 0 ? 'positive' : 'negative'">
              <i :class="stats.speedChange >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(stats.speedChange) }}%
            </p>
          </div>
        </div>

        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>Completion Rate</h3>
            <p class="card-value">{{ stats.completionRate }}%</p>
            <p class="card-change" :class="stats.completionChange >= 0 ? 'positive' : 'negative'">
              <i :class="stats.completionChange >= 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(stats.completionChange) }}%
            </p>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="charts-grid">
        <div class="chart-card">
          <h3>Reading Activity</h3>
          <div class="chart-container">
            <canvas ref="activityChart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <h3>Document Types</h3>
          <div class="chart-container">
            <canvas ref="typesChart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <h3>Reading Speed Trend</h3>
          <div class="chart-container">
            <canvas ref="speedChart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <h3>Completion Rate</h3>
          <div class="chart-container">
            <canvas ref="completionChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Detailed Statistics -->
      <div class="detailed-stats">
        <div class="stats-section">
          <h3>Top Documents</h3>
          <div class="stats-table">
            <table>
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Type</th>
                  <th>Reading Time</th>
                  <th>Completion</th>
                  <th>Speed</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="doc in topDocuments" :key="doc.id">
                  <td>{{ doc.title }}</td>
                  <td>{{ doc.type }}</td>
                  <td>{{ formatDuration(doc.readingTime) }}</td>
                  <td>{{ doc.completion }}%</td>
                  <td>{{ doc.speed }} wpm</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="stats-section">
          <h3>Reading Patterns</h3>
          <div class="patterns-grid">
            <div class="pattern-card">
              <h4>Peak Reading Time</h4>
              <p class="pattern-value">{{ stats.peakTime }}</p>
              <p class="pattern-label">Most active reading period</p>
            </div>
            <div class="pattern-card">
              <h4>Average Session</h4>
              <p class="pattern-value">{{ formatDuration(stats.avgSession) }}</p>
              <p class="pattern-label">Typical reading session length</p>
            </div>
            <div class="pattern-card">
              <h4>Documents per Day</h4>
              <p class="pattern-value">{{ stats.documentsPerDay }}</p>
              <p class="pattern-label">Average documents read daily</p>
            </div>
            <div class="pattern-card">
              <h4>Words per Day</h4>
              <p class="pattern-value">{{ stats.wordsPerDay.toLocaleString() }}</p>
              <p class="pattern-label">Average words read daily</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { Chart } from 'chart.js/auto'
import { useAnalyticsStore } from '@/stores/analytics'

export default {
  name: 'AnalyticsDashboard',
  setup() {
    const analyticsStore = useAnalyticsStore()
    const dateRange = ref('30')
    const activityChart = ref(null)
    const typesChart = ref(null)
    const speedChart = ref(null)
    const completionChart = ref(null)

    const stats = ref({
      totalDocuments: 0,
      documentsChange: 0,
      totalReadingTime: 0,
      readingTimeChange: 0,
      averageSpeed: 0,
      speedChange: 0,
      completionRate: 0,
      completionChange: 0,
      peakTime: '14:00 - 16:00',
      avgSession: 0,
      documentsPerDay: 0,
      wordsPerDay: 0
    })

    const topDocuments = ref([])

    const fetchAnalytics = async () => {
      try {
        const data = await analyticsStore.getAnalytics(dateRange.value)
        stats.value = data.stats
        topDocuments.value = data.topDocuments
        updateCharts(data)
      } catch (err) {
        console.error('Failed to fetch analytics:', err)
      }
    }

    const updateCharts = (data) => {
      // Activity Chart
      new Chart(activityChart.value, {
        type: 'line',
        data: {
          labels: data.activity.labels,
          datasets: [{
            label: 'Reading Time (minutes)',
            data: data.activity.data,
            borderColor: 'var(--color-primary)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })

      // Document Types Chart
      new Chart(typesChart.value, {
        type: 'doughnut',
        data: {
          labels: data.types.labels,
          datasets: [{
            data: data.types.data,
            backgroundColor: [
              'var(--color-primary)',
              'var(--color-secondary)',
              'var(--color-success)',
              'var(--color-warning)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })

      // Reading Speed Chart
      new Chart(speedChart.value, {
        type: 'line',
        data: {
          labels: data.speed.labels,
          datasets: [{
            label: 'Words per Minute',
            data: data.speed.data,
            borderColor: 'var(--color-success)',
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })

      // Completion Rate Chart
      new Chart(completionChart.value, {
        type: 'bar',
        data: {
          labels: data.completion.labels,
          datasets: [{
            label: 'Completion Rate (%)',
            data: data.completion.data,
            backgroundColor: 'var(--color-primary)'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }

    const formatDuration = (minutes) => {
      const hours = Math.floor(minutes / 60)
      const mins = minutes % 60
      return `${hours}h ${mins}m`
    }

    const exportData = async () => {
      try {
        await analyticsStore.exportAnalytics(dateRange.value)
      } catch (err) {
        console.error('Failed to export analytics:', err)
      }
    }

    watch(dateRange, () => {
      fetchAnalytics()
    })

    onMounted(() => {
      fetchAnalytics()
    })

    return {
      dateRange,
      stats,
      topDocuments,
      activityChart,
      typesChart,
      speedChart,
      completionChart,
      formatDuration,
      exportData
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
  padding: 2rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.dashboard-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background-color: var(--color-background);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.card-icon {
  font-size: 2rem;
  color: var(--color-primary);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: var(--color-text-secondary);
}

.card-value {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.card-change {
  margin: 0;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.card-change.positive {
  color: var(--color-success);
}

.card-change.negative {
  color: var(--color-error);
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.chart-card h3 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
}

.chart-container {
  height: 300px;
}

.detailed-stats {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.stats-section {
  background-color: var(--color-background);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.stats-section h3 {
  margin: 0 0 1rem;
  font-size: 1.1rem;
}

.stats-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

th {
  font-weight: 500;
  color: var(--color-text-secondary);
}

.patterns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.pattern-card {
  background-color: var(--color-background-alt);
  border-radius: var(--border-radius);
  padding: 1rem;
}

.pattern-card h4 {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.pattern-value {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
  font-weight: 600;
}

.pattern-label {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-text-tertiary);
}

@media (max-width: 1024px) {
  .detailed-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .dashboard-actions {
    flex-direction: column;
  }

  .date-range {
    width: 100%;
  }

  .filter-select {
    flex: 1;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style> 