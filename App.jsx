import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000/api'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [backendConnected, setBackendConnected] = useState(false)

  const [config, setConfig] = useState({
    requestTimeout: 5000,
    maxRetries: 3,
    healthCheckInterval: 10,
    loadBalancing: 'Round Robin',
  })

  const [savedMessage, setSavedMessage] = useState('')

  const [services, setServices] = useState([
    {
      name: 'User Service',
      instance: 'user-01',
      status: 'Healthy',
      version: 'v1.2',
    },
    {
      name: 'User Service',
      instance: 'user-02',
      status: 'Healthy',
      version: 'v1.2',
    },
    {
      name: 'Order Service',
      instance: 'order-01',
      status: 'Healthy',
      version: 'v2.1',
    },
    {
      name: 'Order Service',
      instance: 'order-02',
      status: 'Healthy',
      version: 'v2.1',
    },
    {
      name: 'Payment Service',
      instance: 'payment-01',
      status: 'Healthy',
      version: 'v1.5',
    },
    {
      name: 'Payment Service',
      instance: 'payment-02',
      status: 'Healthy',
      version: 'v1.5',
    },
    {
      name: 'Notification Service',
      instance: 'notification-01',
      status: 'Healthy',
      version: 'v1.1',
    },
  ])

  const [failureMessage, setFailureMessage] = useState('')

  const [monitoringData, setMonitoringData] = useState({
    uptime: 99.98,
    requestRate: 1248,
    responseTime: 142,
    errorRate: 0.12,
  })

  useEffect(function loadInitialState() {
    async function fetchAll() {
      try {
        const [svcRes, cfgRes, monRes] = await Promise.all([
          fetch(`${API_BASE}/services`),
          fetch(`${API_BASE}/config`),
          fetch(`${API_BASE}/monitoring`),
        ])
        if (svcRes.ok && cfgRes.ok && monRes.ok) {
          const svcJson = await svcRes.json()
          const cfgJson = await cfgRes.json()
          const monJson = await monRes.json()
          setServices(svcJson.data)
          setConfig({
            requestTimeout: cfgJson.data.requestTimeout,
            maxRetries: cfgJson.data.maxRetries,
            healthCheckInterval: cfgJson.data.healthCheckInterval,
            loadBalancing: cfgJson.data.loadBalancing,
          })
          setMonitoringData(monJson.data)
          setBackendConnected(true)
        }
      } catch (err) {
        setBackendConnected(false)
      }
    }
    fetchAll()
  }, [])

  const handleConfigChange = (field, value) => {
    setConfig({
      ...config,
      [field]: value,
    })

    setSavedMessage('')
  }

  const saveConfiguration = async () => {
    try {
      const res = await fetch(`${API_BASE}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })
      if (res.ok) {
        const svcRes = await fetch(`${API_BASE}/services`)
        if (svcRes.ok) {
          const svcJson = await svcRes.json()
          setServices(svcJson.data)
        }
        setBackendConnected(true)
      }
    } catch (err) {
      // Fallback to local state if backend is offline
    }
    setSavedMessage('Configuration updated successfully!')

    setTimeout(() => {
      setSavedMessage('')
    }, 3000)
  }

  const simulateFailure = async (instance) => {
    try {
      const res = await fetch(`${API_BASE}/faults/inject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fault_type: 'INSTANCE_CRASH',
          target_instance: instance,
        }),
      })
      if (res.ok) {
        const svcRes = await fetch(`${API_BASE}/services`)
        if (svcRes.ok) {
          const svcJson = await svcRes.json()
          setServices(svcJson.data)
        }
      }
    } catch (err) {
      setServices((currentServices) =>
        currentServices.map((service) =>
          service.instance === instance
            ? {
                ...service,
                status: 'Failed',
              }
            : service
        )
      )
    }

    setFailureMessage(
      `${instance} has failed and is removed from active routing.`
    )

    setTimeout(() => {
      setFailureMessage('')
    }, 4000)
  }

  const recoverInstance = async (instance) => {
    try {
      const res = await fetch(`${API_BASE}/faults/recover/${instance}`, {
        method: 'POST',
      })
      if (res.ok) {
        const svcRes = await fetch(`${API_BASE}/services`)
        if (svcRes.ok) {
          const svcJson = await svcRes.json()
          setServices(svcJson.data)
        }
      }
    } catch (err) {
      setServices((currentServices) =>
        currentServices.map((service) =>
          service.instance === instance
            ? {
                ...service,
                status: 'Healthy',
              }
            : service
        )
      )
    }

    setFailureMessage(
      `${instance} has recovered and is available again.`
    )

    setTimeout(() => {
      setFailureMessage('')
    }, 4000)
  }

  const refreshMonitoring = async () => {
    try {
      const res = await fetch(`${API_BASE}/monitoring?refresh=true`)
      if (res.ok) {
        const monJson = await res.json()
        setMonitoringData(monJson.data)
        setBackendConnected(true)
        return
      }
    } catch (err) {
      // Fallback to local simulation
    }
    setMonitoringData({
      uptime: Number((99.9 + Math.random() * 0.09).toFixed(2)),
      requestRate: Math.floor(1100 + Math.random() * 400),
      responseTime: Math.floor(120 + Math.random() * 80),
      errorRate: Number((Math.random() * 0.5).toFixed(2)),
    })
  }

  const healthyCount = services.filter(
    (service) => service.status === 'Healthy'
  ).length

  const failedCount = services.filter(
    (service) => service.status === 'Failed'
  ).length


  // =========================
  // DASHBOARD
  // =========================

  const renderDashboard = () => {
    return (
      <>
        <header className="header">
          <div>
            <h1>Service Discovery Dashboard</h1>
            <p>
              Monitor service health, discovery and dynamic configuration
            </p>
          </div>

          <div className="system-status">
            <span className="status-dot"></span>
            System Healthy
          </div>
        </header>

        <section className="stats">

          <div className="stat-card">
            <div className="stat-top">
              <span>Active Services</span>
              <div className="stat-icon blue">◆</div>
            </div>

            <h2>8</h2>
            <p>Currently running</p>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Healthy Instances</span>
              <div className="stat-icon green">✓</div>
            </div>

            <h2>{healthyCount}</h2>

            <p className="positive">
              Available for routing
            </p>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Failed Instances</span>
              <div className="stat-icon red">!</div>
            </div>

            <h2>{failedCount}</h2>

            <p className="failed">
              Need attention
            </p>
          </div>

          <div className="stat-card">
            <div className="stat-top">
              <span>Config Version</span>
              <div className="stat-icon purple">⚙</div>
            </div>

            <h2>v8</h2>
            <p>Latest configuration</p>
          </div>

        </section>


        <section className="section">

          <div className="section-header">

            <h2>Service Instances</h2>

            <button
              className="view-button"
              onClick={() => setCurrentPage('services')}
            >
              View Services
            </button>

          </div>

          <div className="service-table">

            <div className="table-header">
              <span>Service</span>
              <span>Instance</span>
              <span>Status</span>
              <span>Version</span>
            </div>

            {services.slice(0, 5).map((service) => (

              <div
                className="table-row"
                key={service.instance}
              >
                <span>{service.name}</span>
                <span>{service.instance}</span>

                <span
                  className={
                    service.status === 'Healthy'
                      ? 'healthy'
                      : 'failed'
                  }
                >
                  ● {service.status}
                </span>

                <span>{service.version}</span>
              </div>

            ))}

          </div>

        </section>


        <section className="bottom-grid">

          <div className="panel">

            <div className="panel-header">
              <h2>Dynamic Configuration</h2>

              <span className="version">
                v8
              </span>
            </div>

            <div className="config-item">
              <span>Request Timeout</span>
              <strong>
                {config.requestTimeout} ms
              </strong>
            </div>

            <div className="config-item">
              <span>Maximum Retries</span>
              <strong>
                {config.maxRetries}
              </strong>
            </div>

            <div className="config-item">
              <span>Health Check Interval</span>
              <strong>
                {config.healthCheckInterval} sec
              </strong>
            </div>

            <button
              className="primary-button"
              onClick={() =>
                setCurrentPage('configuration')
              }
            >
              Manage Configuration
            </button>

          </div>


          <div className="panel">

            <div className="panel-header">
              <h2>System Status</h2>
            </div>

            <div className="event">

              <span className="event-dot healthy-bg"></span>

              <div>
                <strong>
                  Service registry online
                </strong>

                <p>
                  System operating normally
                </p>
              </div>

            </div>

            <div className="event">

              <span className="event-dot healthy-bg"></span>

              <div>
                <strong>
                  Health checks active
                </strong>

                <p>
                  Every {config.healthCheckInterval} seconds
                </p>
              </div>

            </div>

            <div className="event">

              <span className="event-dot warning-bg"></span>

              <div>
                <strong>
                  Failure simulator ready
                </strong>

                <p>
                  Testing environment
                </p>
              </div>

            </div>

          </div>

        </section>
      </>
    )
  }


  // =========================
  // SERVICES PAGE
  // =========================

  const renderServices = () => {
    return (
      <>
        <header className="header">

          <div>
            <h1>Services</h1>

            <p>
              Registered service instances and their health status
            </p>
          </div>

          <div className="system-status">

            <span className="status-dot"></span>

            Registry Online

          </div>

        </header>


        <section className="stats">

          <div className="stat-card">

            <div className="stat-top">
              <span>Total Instances</span>

              <div className="stat-icon blue">
                ◆
              </div>
            </div>

            <h2>{services.length}</h2>

            <p>
              Registered instances
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Healthy</span>

              <div className="stat-icon green">
                ✓
              </div>
            </div>

            <h2>{healthyCount}</h2>

            <p className="positive">
              Available instances
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Failed</span>

              <div className="stat-icon red">
                !
              </div>
            </div>

            <h2>{failedCount}</h2>

            <p className="failed">
              Unavailable instances
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Health Check</span>

              <div className="stat-icon purple">
                ↻
              </div>
            </div>

            <h2>
              {config.healthCheckInterval}s
            </h2>

            <p>
              Check interval
            </p>

          </div>

        </section>


        <section className="section">

          <div className="section-header">

            <h2>Registered Services</h2>

            <button className="view-button">
              Refresh
            </button>

          </div>


          <div className="service-table">

            <div className="table-header">

              <span>Service</span>

              <span>Instance</span>

              <span>Status</span>

              <span>Version</span>

            </div>


            {services.map((service) => (

              <div
                className="table-row"
                key={service.instance}
              >

                <span>
                  <strong>
                    {service.name}
                  </strong>
                </span>

                <span>
                  {service.instance}
                </span>

                <span
                  className={
                    service.status === 'Healthy'
                      ? 'healthy'
                      : 'failed'
                  }
                >
                  ● {service.status}
                </span>

                <span>
                  {service.version}
                </span>

              </div>

            ))}

          </div>

        </section>
      </>
    )
  }


  // =========================
  // CONFIGURATION PAGE
  // =========================

  const renderConfiguration = () => {
    return (
      <>
        <header className="header">

          <div>
            <h1>
              Dynamic Configuration
            </h1>

            <p>
              Modify service configuration
              without restarting services
            </p>
          </div>

          <div className="system-status">

            <span className="status-dot"></span>

            Configuration Active

          </div>

        </header>


        <section className="stats">

          <div className="stat-card">

            <div className="stat-top">
              <span>Configuration Version</span>

              <div className="stat-icon purple">
                ⚙
              </div>
            </div>

            <h2>v8</h2>

            <p>
              Current version
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Services Using Config</span>

              <div className="stat-icon blue">
                ◆
              </div>
            </div>

            <h2>8</h2>

            <p>
              Active services
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Health Interval</span>

              <div className="stat-icon green">
                ✓
              </div>
            </div>

            <h2>
              {config.healthCheckInterval}s
            </h2>

            <p>
              Current setting
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Config Status</span>

              <div className="stat-icon green">
                ✓
              </div>
            </div>

            <h2>Active</h2>

            <p className="positive">
              Synchronized
            </p>

          </div>

        </section>


        <section className="configuration-panel">

          <div className="panel-header">

            <div>

              <h2>
                Service Configuration
              </h2>

              <p className="panel-description">
                Change values and apply the
                new configuration
              </p>

            </div>

            <span className="version">
              v8
            </span>

          </div>


          <div className="form-group">

            <label>
              Request Timeout
            </label>

            <p>
              Maximum time allowed for a
              service request.
            </p>

            <div className="input-with-unit">

              <input
                type="number"
                value={config.requestTimeout}
                onChange={(e) =>
                  handleConfigChange(
                    'requestTimeout',
                    e.target.value
                  )
                }
              />

              <span>
                milliseconds
              </span>

            </div>

          </div>


          <div className="form-group">

            <label>
              Maximum Retries
            </label>

            <p>
              Number of times a failed
              request should be retried.
            </p>

            <div className="input-with-unit">

              <input
                type="number"
                value={config.maxRetries}
                onChange={(e) =>
                  handleConfigChange(
                    'maxRetries',
                    e.target.value
                  )
                }
              />

              <span>
                retries
              </span>

            </div>

          </div>


          <div className="form-group">

            <label>
              Health Check Interval
            </label>

            <p>
              Time between service health
              checks.
            </p>

            <div className="input-with-unit">

              <input
                type="number"
                value={config.healthCheckInterval}
                onChange={(e) =>
                  handleConfigChange(
                    'healthCheckInterval',
                    e.target.value
                  )
                }
              />

              <span>
                seconds
              </span>

            </div>

          </div>


          <div className="form-group">

            <label>
              Load Balancing Strategy
            </label>

            <p>
              Strategy used when selecting
              a service instance.
            </p>

            <select
              value={config.loadBalancing}
              onChange={(e) =>
                handleConfigChange(
                  'loadBalancing',
                  e.target.value
                )
              }
            >

              <option>
                Round Robin
              </option>

              <option>
                Random
              </option>

              <option>
                Least Connections
              </option>

            </select>

          </div>


          <div className="configuration-actions">

            <button
              className="primary-button"
              onClick={saveConfiguration}
            >
              Save Configuration
            </button>

            {savedMessage && (
              <span className="success-message">
                ✓ {savedMessage}
              </span>
            )}

          </div>

        </section>
      </>
    )
  }


  // =========================
  // FAILURE PAGE
  // =========================

  const renderFailures = () => {
    return (
      <>
        <header className="header">

          <div>
            <h1>
              Failure Simulation
            </h1>

            <p>
              Simulate service failures and
              observe system recovery
            </p>
          </div>

          <div className="system-status">

            <span className="status-dot"></span>

            Failure Testing Mode

          </div>

        </header>


        <section className="stats">

          <div className="stat-card">

            <div className="stat-top">
              <span>Total Instances</span>

              <div className="stat-icon blue">
                ◆
              </div>
            </div>

            <h2>
              {services.length}
            </h2>

            <p>
              Registered instances
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Healthy Instances</span>

              <div className="stat-icon green">
                ✓
              </div>
            </div>

            <h2>
              {healthyCount}
            </h2>

            <p className="positive">
              Available for routing
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Failed Instances</span>

              <div className="stat-icon red">
                !
              </div>
            </div>

            <h2>
              {failedCount}
            </h2>

            <p className="failed">
              Removed from routing
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">
              <span>Retries</span>

              <div className="stat-icon purple">
                ↻
              </div>
            </div>

            <h2>
              {config.maxRetries}
            </h2>

            <p>
              Maximum retries
            </p>

          </div>

        </section>


        {failureMessage && (

          <div className="failure-message">

            <span>⚠</span>

            {failureMessage}

          </div>

        )}


        <section className="section">

          <div className="section-header">

            <div>

              <h2>
                Service Instances
              </h2>

              <p className="section-description">
                Use the controls to simulate
                partial failures.
              </p>

            </div>

          </div>


          <div className="failure-table">

            <div className="failure-table-header">

              <span>Service</span>

              <span>Instance</span>

              <span>Status</span>

              <span>Action</span>

            </div>


            {services.map((service) => (

              <div
                className="failure-table-row"
                key={service.instance}
              >

                <span>
                  <strong>
                    {service.name}
                  </strong>
                </span>

                <span>
                  {service.instance}
                </span>

                <span
                  className={
                    service.status === 'Healthy'
                      ? 'healthy'
                      : 'failed'
                  }
                >
                  ● {service.status}
                </span>

                <span>

                  {service.status === 'Healthy' ? (

                    <button
                      className="failure-button"
                      onClick={() =>
                        simulateFailure(
                          service.instance
                        )
                      }
                    >
                      Simulate Failure
                    </button>

                  ) : (

                    <button
                      className="recover-button"
                      onClick={() =>
                        recoverInstance(
                          service.instance
                        )
                      }
                    >
                      Recover Instance
                    </button>

                  )}

                </span>

              </div>

            ))}

          </div>

        </section>


        <section className="bottom-grid">

          <div className="panel">

            <div className="panel-header">

              <h2>
                Failure Handling
              </h2>

            </div>

            <div className="config-item">

              <span>
                Failed instance
              </span>

              <strong className="failed">
                Removed from routing
              </strong>

            </div>

            <div className="config-item">

              <span>
                Healthy instances
              </span>

              <strong className="healthy">
                Continue serving
              </strong>

            </div>

            <div className="config-item">

              <span>
                Maximum retries
              </span>

              <strong>
                {config.maxRetries}
              </strong>

            </div>

            <div className="config-item">

              <span>
                Health check
              </span>

              <strong>
                {config.healthCheckInterval}s
              </strong>

            </div>

          </div>


          <div className="panel">

            <div className="panel-header">

              <h2>
                What Happens?
              </h2>

            </div>

            <div className="event">

              <span className="event-dot failed-bg"></span>

              <div>

                <strong>
                  Instance failure detected
                </strong>

                <p>
                  Failed instance becomes
                  unavailable
                </p>

              </div>

            </div>

            <div className="event">

              <span className="event-dot warning-bg"></span>

              <div>

                <strong>
                  Routing updated
                </strong>

                <p>
                  Requests avoid failed
                  instance
                </p>

              </div>

            </div>

            <div className="event">

              <span className="event-dot healthy-bg"></span>

              <div>

                <strong>
                  Other instances continue
                </strong>

                <p>
                  Service remains available
                </p>

              </div>

            </div>

          </div>

        </section>
      </>
    )
  }


  // =========================
  // MONITORING PAGE
  // =========================

  const renderMonitoring = () => {
    return (
      <>
        <header className="header">

          <div>
            <h1>
              Monitoring
            </h1>

            <p>
              Monitor system performance,
              availability and service health
            </p>
          </div>

          <div className="monitoring-header-actions">

            <div className="system-status">

              <span className="status-dot"></span>

              Monitoring Active

            </div>

            <button
              className="refresh-button"
              onClick={refreshMonitoring}
            >
              ↻ Refresh
            </button>

          </div>

        </header>


        {/* Monitoring Statistics */}

        <section className="stats">

          <div className="stat-card">

            <div className="stat-top">

              <span>
                System Uptime
              </span>

              <div className="stat-icon green">
                ✓
              </div>

            </div>

            <h2>
              {monitoringData.uptime}%
            </h2>

            <p className="positive">
              Service availability
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">

              <span>
                Request Rate
              </span>

              <div className="stat-icon blue">
                ↗
              </div>

            </div>

            <h2>
              {monitoringData.requestRate}
            </h2>

            <p>
              Requests / minute
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">

              <span>
                Response Time
              </span>

              <div className="stat-icon purple">
                ◷
              </div>

            </div>

            <h2>
              {monitoringData.responseTime}
              <small> ms</small>
            </h2>

            <p>
              Average response
            </p>

          </div>


          <div className="stat-card">

            <div className="stat-top">

              <span>
                Error Rate
              </span>

              <div className="stat-icon red">
                !
              </div>

            </div>

            <h2>
              {monitoringData.errorRate}%
            </h2>

            <p className="failed">
              Request errors
            </p>

          </div>

        </section>


        {/* Service Health */}

        <section className="section">

          <div className="section-header">

            <div>

              <h2>
                Service Health
              </h2>

              <p className="section-description">
                Current health status of registered
                service instances
              </p>

            </div>

            <span className="healthy-summary">
              {healthyCount} Healthy
            </span>

          </div>


          <div className="monitoring-services">

            {services.map((service) => (

              <div
                className="monitoring-service"
                key={service.instance}
              >

                <div className="monitoring-service-info">

                  <div
                    className={
                      service.status === 'Healthy'
                        ? 'health-indicator healthy-indicator'
                        : 'health-indicator failed-indicator'
                    }
                  ></div>

                  <div>

                    <strong>
                      {service.name}
                    </strong>

                    <p>
                      {service.instance}
                    </p>

                  </div>

                </div>


                <div className="monitoring-service-status">

                  <span
                    className={
                      service.status === 'Healthy'
                        ? 'healthy'
                        : 'failed'
                    }
                  >
                    {service.status}
                  </span>

                  <span className="service-version">
                    {service.version}
                  </span>

                </div>

              </div>

            ))}

          </div>

        </section>


        {/* Monitoring Details */}

        <section className="bottom-grid">

          <div className="panel">

            <div className="panel-header">

              <h2>
                Performance
              </h2>

              <span className="version">
                Live
              </span>

            </div>


            <div className="monitoring-progress">

              <div className="progress-header">

                <span>
                  CPU Utilization
                </span>

                <strong>
                  42%
                </strong>

              </div>

              <div className="progress-bar">

                <div
                  className="progress-fill"
                  style={{ width: '42%' }}
                ></div>

              </div>

            </div>


            <div className="monitoring-progress">

              <div className="progress-header">

                <span>
                  Memory Utilization
                </span>

                <strong>
                  58%
                </strong>

              </div>

              <div className="progress-bar">

                <div
                  className="progress-fill"
                  style={{ width: '58%' }}
                ></div>

              </div>

            </div>


            <div className="monitoring-progress">

              <div className="progress-header">

                <span>
                  Request Capacity
                </span>

                <strong>
                  71%
                </strong>

              </div>

              <div className="progress-bar">

                <div
                  className="progress-fill"
                  style={{ width: '71%' }}
                ></div>

              </div>

            </div>

          </div>


          <div className="panel">

            <div className="panel-header">

              <h2>
                Recent Events
              </h2>

            </div>


            <div className="event">

              <span className="event-dot healthy-bg"></span>

              <div>

                <strong>
                  Monitoring service active
                </strong>

                <p>
                  Health monitoring is running
                </p>

              </div>

            </div>


            <div className="event">

              <span className="event-dot healthy-bg"></span>

              <div>

                <strong>
                  All healthy instances available
                </strong>

                <p>
                  Services are ready for routing
                </p>

              </div>

            </div>


            <div className="event">

              <span className="event-dot warning-bg"></span>

              <div>

                <strong>
                  Monitoring refresh enabled
                </strong>

                <p>
                  Click refresh to update metrics
                </p>

              </div>

            </div>

          </div>

        </section>

      </>
    )
  }


  // =========================
  // APPLICATION
  // =========================

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">

        <h2>
          ServiceHub
        </h2>


        <nav>

          <button
            className={
              currentPage === 'dashboard'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={() =>
              setCurrentPage('dashboard')
            }
          >
            Dashboard
          </button>


          <button
            className={
              currentPage === 'services'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={() =>
              setCurrentPage('services')
            }
          >
            Services
          </button>


          <button
            className={
              currentPage === 'configuration'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={() =>
              setCurrentPage('configuration')
            }
          >
            Configuration
          </button>


          <button
            className={
              currentPage === 'failures'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={() =>
              setCurrentPage('failures')
            }
          >
            Failures
          </button>


          <button
            className={
              currentPage === 'monitoring'
                ? 'nav-item active'
                : 'nav-item'
            }
            onClick={() =>
              setCurrentPage('monitoring')
            }
          >
            Monitoring
          </button>

        </nav>


        <div className="sidebar-footer">

          <span className="online-dot"></span>

          System Online

        </div>

      </aside>


      {/* MAIN CONTENT */}

      <main className="main-content">

        {currentPage === 'dashboard' &&
          renderDashboard()}

        {currentPage === 'services' &&
          renderServices()}

        {currentPage === 'configuration' &&
          renderConfiguration()}

        {currentPage === 'failures' &&
          renderFailures()}

        {currentPage === 'monitoring' &&
          renderMonitoring()}

      </main>

    </div>
  )
}

export default App