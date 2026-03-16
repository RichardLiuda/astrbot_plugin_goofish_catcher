import {
	Alert,
	AppBar,
	Box,
	Button,
	CircularProgress,
	CssBaseline,
	Drawer,
	LinearProgress,
	Snackbar,
	Stack,
	ThemeProvider,
	Toolbar,
	Typography,
	createRoot,
	html,
	useEffect,
	useMediaQuery,
	useState
} from './modules/deps.js'
import { LoginView } from './modules/components.js'
import { NAV_ITEMS } from './modules/constants.js'
import {
	ConfigPage,
	DashboardPage,
	ItemsPage,
	RuntimePage,
	SubscriptionsPage
} from './modules/pages/index.js'
import { darkTheme, lightTheme } from './modules/theme.js'
import {
	api,
	cx,
	formatDuration,
	formatTs,
	getRoute,
	setRoute
} from './modules/utils.js'

const SHELL_MOBILE_QUERY = '(max-width: 1119px)'
const MONITOR_IDLE_INTERVAL_MS = 8000
const MONITOR_ACTIVE_INTERVAL_MS = 2000
const DEFAULT_TEMP_QUERY = {
	keyword: '',
	pages: 1,
	preview: null,
	loading: false
}

function App() {
	const [route, setRouteState] = useState(getRoute())
	const [authenticated, setAuthenticated] = useState(false)
	const [booting, setBooting] = useState(true)
	const [loginLoading, setLoginLoading] = useState(false)
	const [loginError, setLoginError] = useState('')
	const [drawerOpen, setDrawerOpen] = useState(false)
	const [snack, setSnack] = useState({
		open: false,
		message: '',
		severity: 'success'
	})
	const [monitorCollapsed, setMonitorCollapsed] = useState(false)
	const [temporaryQuery, setTemporaryQuery] = useState(DEFAULT_TEMP_QUERY)
	const [liveMonitor, setLiveMonitor] = useState({
		summary: null,
		items: []
	})
	const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)')
	const activeTheme = prefersDarkMode ? darkTheme : lightTheme
	const isMobile = useMediaQuery(SHELL_MOBILE_QUERY)

	useEffect(() => {
		document.documentElement.dataset.theme = prefersDarkMode ? 'dark' : 'light'
	}, [prefersDarkMode])

	function notify(message, severity = 'success') {
		setSnack({ open: true, message, severity })
	}

	function updateTemporaryQuery(patch) {
		setTemporaryQuery((current) => ({
			...current,
			...patch
		}))
	}

	async function runTemporaryQuery() {
		const keyword = String(temporaryQuery.keyword || '').trim()
		if (!keyword || temporaryQuery.loading) {
			return
		}

		updateTemporaryQuery({ loading: true })
		try {
			const payload = await api('/api/query', {
				method: 'POST',
				body: {
					keyword,
					pages: Number(temporaryQuery.pages || 1)
				}
			})
			setTemporaryQuery((current) => ({
				...current,
				keyword,
				pages: Number(current.pages || 1),
				preview: payload.preview,
				loading: false
			}))
			notify('临时查询已完成', 'success')
		} catch (error) {
			updateTemporaryQuery({ loading: false })
			notify(error.message, 'error')
		}
	}

	async function boot() {
		try {
			await api('/api/overview')
			setAuthenticated(true)
		} catch (error) {
			if (error.code !== 'UNAUTHORIZED') {
				notify(error.message, 'error')
			}
			setAuthenticated(false)
		} finally {
			setBooting(false)
		}
	}

	useEffect(() => {
		boot()
		const onHashChange = () => setRouteState(getRoute())
		window.addEventListener('hashchange', onHashChange)
		return () => window.removeEventListener('hashchange', onHashChange)
	}, [])

	useEffect(() => {
		if (!authenticated) {
			setLiveMonitor({
				summary: null,
				items: []
			})
			setTemporaryQuery(DEFAULT_TEMP_QUERY)
			return undefined
		}

		let cancelled = false
		let timer = null

		async function loadMonitor() {
			let nextDelay = MONITOR_IDLE_INTERVAL_MS

			try {
				const monitorPayload = await api('/api/activity-monitor')
				const hasActiveWork =
					Number(monitorPayload?.summary?.active_count || 0) > 0 ||
					Number(monitorPayload?.summary?.queue_size || 0) > 0 ||
					Number(monitorPayload?.summary?.inflight || 0) > 0

				if (hasActiveWork) {
					nextDelay = MONITOR_ACTIVE_INTERVAL_MS
				}

				if (!cancelled) {
					setLiveMonitor(monitorPayload)
				}
			} catch (error) {
				if (error.code === 'UNAUTHORIZED') {
					setAuthenticated(false)
					return
				}
			} finally {
				if (!cancelled) {
					timer = window.setTimeout(loadMonitor, nextDelay)
				}
			}
		}

		loadMonitor()

		return () => {
			cancelled = true
			if (timer) {
				window.clearTimeout(timer)
			}
		}
	}, [authenticated])

	async function login(apiKey) {
		setLoginLoading(true)
		setLoginError('')
		try {
			await api('/api/admin/login', {
				method: 'POST',
				body: { api_key: apiKey }
			})
			setAuthenticated(true)
			notify('登录成功', 'success')
			boot()
		} catch (error) {
			setLoginError(error.message)
		} finally {
			setLoginLoading(false)
		}
	}

	async function logout() {
		try {
			await api('/api/admin/logout', { method: 'POST' })
		} catch (_) {
			// ignore logout failure
		}
		setAuthenticated(false)
	}

	const monitorSummary = liveMonitor.summary || {}
	const monitorItems = liveMonitor.items || []
	const monitorActive =
		Number(monitorSummary.active_count || 0) > 0 ||
		Number(monitorSummary.queue_size || 0) > 0 ||
		Number(monitorSummary.inflight || 0) > 0
	const monitorLead = monitorItems[0] || null
	const collapsedSummary = monitorLead
		? `${monitorLead.phase_label} · ${monitorLead.keyword}`
		: `排队 ${monitorSummary.queue_size || 0} · 活跃 ${monitorSummary.active_count || 0}`

	useEffect(() => {
		if (!monitorActive) {
			setMonitorCollapsed(false)
		}
	}, [monitorActive])

	if (booting) {
		return html`
			<${ThemeProvider} theme=${activeTheme}>
				<${CssBaseline} />
				<${Box}
					sx=${{
						minHeight: '100vh',
						display: 'grid',
						placeItems: 'center'
					}}
				>
					<${CircularProgress} />
				<//>
			<//>
		`
	}

	if (!authenticated) {
		return html`
			<${ThemeProvider} theme=${activeTheme}>
				<${CssBaseline} />
				<${LoginView}
					loading=${loginLoading}
					error=${loginError}
					onLogin=${login}
				/>
			<//>
		`
	}

	const currentNav =
		NAV_ITEMS.find((item) => item.key === route) || NAV_ITEMS[0]

	const sidebarContent = html`
		<${Stack} spacing=${3.5}>
			<div className="brand-row">
				<div className="brand-mark">
					<img
						src="/assets/logo.png"
						alt="Goofish Catcher logo"
						className="brand-mark-img"
					/>
				</div>
				<div>
					<${Typography} variant="subtitle1">Goofish Catcher<//>
					<${Typography} variant="body2" color="text.secondary"
						>管理后台<//
					>
				</div>
			</div>

			<div className="nav-list">
				${NAV_ITEMS.map(
					(item) => html`
						<button
							type="button"
							key=${item.key}
							onClick=${() => {
								setRoute(item.key)
								setRouteState(item.key)
								setDrawerOpen(false)
							}}
							className=${cx(
								'sidebar-nav-button',
								route === item.key && 'is-active'
							)}
						>
							<div className="sidebar-nav-title">
								${item.label}
							</div>
							<div className="sidebar-nav-desc">
								${item.description}
							</div>
						</button>
					`
				)}
			</div>
		<//>
	`

	return html`
		<${ThemeProvider} theme=${activeTheme}>
			<${CssBaseline} />
			<div className="app-shell">
				${isMobile
					? html`
							<${Drawer}
								open=${drawerOpen}
								onClose=${() => setDrawerOpen(false)}
								hideBackdrop=${true}
								ModalProps=${{
									keepMounted: true,
									disableAutoFocus: true,
									disableEnforceFocus: true,
									disableRestoreFocus: true,
									disableScrollLock: true
								}}
								sx=${{
									pointerEvents: 'none'
								}}
								PaperProps=${{
									sx: {
										width: {
											xs: 'calc(100vw - 32px)',
											sm: 320
										},
										maxWidth: '100vw',
										top: { xs: 16, sm: 20 },
										left: { xs: 16, sm: 20 },
										right: 'auto',
										bottom: 'auto',
										height: 'auto',
										maxHeight: 'calc(100vh - 32px)',
										background: 'transparent',
										border: 'none',
										boxShadow: 'none',
										overflow: 'visible',
										pointerEvents: 'none',
										p: 0
									}
								}}
							>
								<div className="app-sidebar mobile-sidebar">
									${sidebarContent}
								</div>
							<//>
						`
					: html`
							<div className="app-sidebar desktop-sidebar">
								${sidebarContent}
							</div>
						`}

				<div className="app-main">
					<div className="app-main-inner">
						<${AppBar}
							position="sticky"
							elevation=${0}
							className="topbar"
							sx=${{ top: { xs: 16, sm: 20, lg: 32 } }}
						>
							<${Toolbar}
								sx=${{ minHeight: 78, px: { xs: 2.25, md: 3 } }}
							>
								${isMobile
									? html`
											<${Button}
												variant="outlined"
												size="small"
												onClick=${() =>
													setDrawerOpen((current) => !current)}
												sx=${{ mr: 1.5 }}
											>
												${drawerOpen ? '收起导航' : '导航'}
											<//>
										`
									: null}
								<${Box} sx=${{ flex: 1, minWidth: 0 }}>
									<${Typography} variant="h6"
										>${currentNav.label}<//
									>
								<//>
								<div className="topbar-actions">
									<div className="topbar-description">
										${currentNav.description}
									</div>
									<${Button} onClick=${logout}>退出登录<//>
								</div>
							<//>
						<//>

						<div
							className=${cx(
								'page-content',
								monitorActive && 'has-live-monitor',
								monitorActive &&
									monitorCollapsed &&
									'has-live-monitor-collapsed'
							)}
						>
							${route === 'dashboard'
								? html`<${DashboardPage}
										notify=${notify}
										temporaryQuery=${temporaryQuery}
										onTemporaryQueryChange=${updateTemporaryQuery}
										onRunTemporaryQuery=${runTemporaryQuery}
									/>`
								: null}
							${route === 'subscriptions'
								? html`<${SubscriptionsPage}
										notify=${notify}
									/>`
								: null}
							${route === 'items'
								? html`<${ItemsPage} notify=${notify} />`
								: null}
							${route === 'runtime'
								? html`<${RuntimePage} notify=${notify} />`
								: null}
							${route === 'config'
								? html`<${ConfigPage} notify=${notify} />`
								: null}
						</div>
					</div>
				</div>
			</div>

			${monitorActive
				? html`
						<div
							className=${cx(
								'floating-monitor',
								monitorCollapsed && 'is-collapsed'
							)}
						>
							<div className="floating-monitor-shell">
								<div className="floating-monitor-head">
									<div>
										<div className="floating-monitor-title">
											<span className="monitor-pulse"></span>
											检查进行中
										</div>
										<div className="floating-monitor-subtitle">
											${monitorCollapsed
												? collapsedSummary
												: monitorSummary.scheduler_running
													? '抓取与分析阶段会在这里实时更新'
													: '存在排队或执行中的检查任务'}
										</div>
									</div>
									<div className="floating-monitor-actions">
										<${Button}
											size="small"
											variant="text"
											onClick=${() => {
												setRoute('runtime')
												setRouteState('runtime')
											}}
										>
											查看详情
										<//>
										<${Button}
											size="small"
											variant="text"
											onClick=${() =>
												setMonitorCollapsed((current) => !current)}
										>
											${monitorCollapsed ? '展开监控' : '收起监控'}
										<//>
									</div>
								</div>

								<div className="floating-monitor-body">
									<div className="floating-monitor-stats">
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												活跃任务
											</span>
											<strong>
												${monitorSummary.active_count || 0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												抓取中
											</span>
											<strong>
												${monitorSummary.fetching_count || 0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												预筛中
											</span>
											<strong>
												${monitorSummary.prefiltering_count || 0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												分析中
											</span>
											<strong>
												${monitorSummary.analyzing_count || 0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												队列
											</span>
											<strong>
												${monitorSummary.queue_size || 0}
											</strong>
										</div>
										<div className="floating-monitor-stat">
											<span className="floating-monitor-label">
												Workers
											</span>
											<strong>
												${monitorSummary.workers || 0}
											</strong>
										</div>
									</div>

									${monitorItems.length
										? html`
												<div className="floating-monitor-list">
													${monitorItems.map((item) => {
														const elapsedSec = Math.max(
															1,
															(monitorSummary.updated_at || 0) -
																item.started_at
														)
														return html`
															<div
																className="floating-monitor-item"
																key=${item.task_id}
															>
																<div className="floating-monitor-item-head">
																	<div className="floating-monitor-item-main">
																		<div className="floating-monitor-item-title">
																			${item.keyword}
																		</div>
																		<div className="floating-monitor-item-meta">
																			${item.source_label} ·
																			${item.phase_label} ·
																			${item.provider_mode}
																		</div>
																	</div>
																	<div className="floating-monitor-phase">
																		${item.progress_pct}%
																	</div>
																</div>
																<${LinearProgress}
																	variant="determinate"
																	value=${item.progress_pct}
																	sx=${{
																		mt: 1.25,
																		height: 8,
																		borderRadius: 999
																	}}
																/>
																${item.message
																	? html`
																			<div className="floating-monitor-item-note">
																				${item.message}
																			</div>
																		`
																	: null}
																<div className="floating-monitor-item-foot">
																	<span>
																		${item.umo || '未绑定 UMO'}
																	</span>
																	<span>
																		开始于
																		${formatTs(
																			item.started_at
																		)}
																	</span>
																	<span>
																		已运行
																		${formatDuration(
																			elapsedSec
																		)}
																	</span>
																</div>
															</div>
														`
													})}
												</div>
											`
										: html`
												<div className="floating-monitor-empty">
													任务已入队，等待开始抓取...
												</div>
											`}
								</div>
							</div>
						</div>
					`
				: null}

			<${Snackbar}
				open=${snack.open}
				autoHideDuration=${3200}
				onClose=${() =>
					setSnack((current) => ({ ...current, open: false }))}
			>
				<${Alert}
					severity=${snack.severity}
					variant="filled"
					onClose=${() =>
						setSnack((current) => ({ ...current, open: false }))}
				>
					${snack.message}
				<//>
			<//>
		<//>
	`
}

createRoot(document.getElementById('root')).render(html`<${App} />`)
