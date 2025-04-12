<template>
  <div class="analytics-dashboard">
    <!-- Summary Cards -->
    <div class="summary-cards">
      <div class="card">
        <div class="card-header">
          <i class="fas fa-book"></i>
          <h3>Total Documents</h3>
        </div>
        <div class="card-body">
          <div class="stat-value">{{ totalDocuments }}</div>
          <div class="stat-change" :class="documentsChange >= 0 ? 'positive' : 'negative'">
            {{ documentsChange }}% from last month
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <i class="fas fa-clock"></i>
          <h3>Total Reading Time</h3>
        </div>
        <div class="card-body">
          <div class="stat-value">{{ formatDuration(totalReadingTime) }}</div>
          <div class="stat-change" :class="readingTimeChange >= 0 ? 'positive' : 'negative'">
            {{ readingTimeChange }}% from last month
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <i class="fas fa-tachometer-alt"></i>
          <h3>Average Reading Speed</h3>
        </div>
        <div class="card-body">
          <div class="stat-value">{{ averageReadingSpeed }} pages/hour</div>
          <div class="stat-change" :class="speedChange >= 0 ? 'positive' : 'negative'">
            {{ speedChange }}% from last month
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <i class="fas fa-check-circle"></i>
          <h3>Completion Rate</h3>
        </div>
        <div class="card-body">
          <div class="stat-value">{{ completionRate }}%</div>
          <div class="stat-change" :class="completionChange >= 0 ? 'positive' : 'negative'">
            {{ completionChange }}% from last month
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="charts">
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
      <div class="top-documents">
        <h3>Top Documents</h3>
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Type</th>
              <th>Reading Time</th>
              <th>Completion</th>
              <th>Last Read</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in topDocuments" :key="doc.id">
              <td>{{ doc.title }}</td>
              <td>{{ doc.type }}</td>
              <td>{{ formatDuration(doc.readingTime) }}</td>
              <td>{{ doc.completion }}%</td>
              <td>{{ formatDate(doc.lastRead) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="reading-patterns">
        <h3>Reading Patterns</h3>
        <div class="patterns-grid">
          <div class="pattern-card" v-for="(pattern, index) in readingPatterns" :key="index">
            <h4>{{ pattern.title }}</h4>
            <p>{{ pattern.description }}</p>
            <div class="pattern-metrics">
              <div class="metric">
                <span class="label">Frequency</span>
                <span class="value">{{ pattern.frequency }}%</span>
              </div>
              <div class="metric">
                <span class="label">Impact</span>
                <span class="value">{{ pattern.impact }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Controls -->
    <div class="export-controls">
      <button class="btn btn-primary" @click="exportData">
        <i class="fas fa-download"></i> Export Data
      </button>
      <div class="date-range">
        <label>Date Range:</label>
        <select v-model="dateRange">
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="custom">Custom Range</option>
        </select>
        <div v-if="dateRange === 'custom'" class="custom-range">
          <input type="date" v-model="startDate" />
          <input type="date" v-model="endDate" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { Chart } from 'chart.js/auto'
import { useAnalyticsStore } from '@/stores/analytics'
import { formatDuration, formatDate } from '@/utils/formatters'

export default {
  name: 'AnalyticsDashboard',
  setup() {
    const analyticsStore = useAnalyticsStore()
    const activityChart = ref(null)
    const typesChart = ref(null)
    const speedChart = ref(null)
    const completionChart = ref(null)
    const dateRange = ref('30')
    const startDate = ref('')
    const endDate = ref('')

    // Fetch analytics data
    const fetchAnalytics = async () => {
      try {
        await analyticsStore.getAnalytics({
          dateRange: dateRange.value,
          startDate: startDate.value,
          endDate: endDate.value
        })
      } catch (error) {
        console.error('Error fetching analytics:', error)
      }
    }

    // Initialize charts
    const initCharts = () => {
      // Activity Chart
      new Chart(activityChart.value, {
        type: 'line',
        data: {
          labels: analyticsStore.activityData.labels,
          datasets: [{
            label: 'Reading Time',
            data: analyticsStore.activityData.values,
            borderColor: '#4CAF50',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })

      // Types Chart
      new Chart(typesChart.value, {
        type: 'doughnut',
        data: {
          labels: analyticsStore.typesData.labels,
          datasets: [{
            data: analyticsStore.typesData.values,
            backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })

      // Speed Chart
      new Chart(speedChart.value, {
        type: 'line',
        data: {
          labels: analyticsStore.speedData.labels,
          datasets: [{
            label: 'Reading Speed',
            data: analyticsStore.speedData.values,
            borderColor: '#FF6384',
            tension: 0.1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })

      // Completion Chart
      new Chart(completionChart.value, {
        type: 'bar',
        data: {
          labels: analyticsStore.completionData.labels,
          datasets: [{
            label: 'Completion Rate',
            data: analyticsStore.completionData.values,
            backgroundColor: '#36A2EB'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      })
    }

    // Export data
    const exportData = async () => {
      try {
        await analyticsStore.exportData({
          dateRange: dateRange.value,
          startDate: startDate.value,
          endDate: endDate.value
        })
      } catch (error) {
        console.error('Error exporting data:', error)
      }
    }

    // Watch date range changes
    watch(dateRange, () => {
      fetchAnalytics()
    })

    onMounted(() => {
      fetchAnalytics()
      initCharts()
    })

    return {
      activityChart,
      typesChart,
      speedChart,
      completionChart,
      dateRange,
      startDate,
      endDate,
      totalDocuments: computed(() => analyticsStore.totalDocuments),
      documentsChange: computed(() => analyticsStore.documentsChange),
      totalReadingTime: computed(() => analyticsStore.totalReadingTime),
      readingTimeChange: computed(() => analyticsStore.readingTimeChange),
      averageReadingSpeed: computed(() => analyticsStore.averageReadingSpeed),
      speedChange: computed(() => analyticsStore.speedChange),
      completionRate: computed(() => analyticsStore.completionRate),
      completionChange: computed(() => analyticsStore.completionChange),
      topDocuments: computed(() => analyticsStore.topDocuments),
      readingPatterns: computed(() => analyticsStore.readingPatterns),
      formatDuration,
      formatDate,
      exportData
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
  padding: 2rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.card-header i {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.card-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--text-color);
}

.stat-change {
  font-size: 0.9rem;
}

.stat-change.positive {
  color: var(--success-color);
}

.stat-change.negative {
  color: var(--error-color);
}

.charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.chart-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.chart-container {
  height: 300px;
  position: relative;
}

.detailed-stats {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: var(--surface-color);
  border-radius: var(--border-radius);
  overflow: hidden;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background: var(--background-color);
  font-weight: 600;
}

.patterns-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.pattern-card {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.pattern-card h4 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.pattern-metrics {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric .label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.metric .value {
  font-weight: 600;
  color: var(--text-color);
}

.export-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-sm);
}

.date-range {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.custom-range {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .analytics-dashboard {
    padding: 1rem;
  }

  .charts {
    grid-template-columns: 1fr;
  }

  .export-controls {
    flex-direction: column;
    gap: 1rem;
  }

  .date-range {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style> 