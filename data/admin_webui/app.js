import {
	Alert,
	AppBar,
	Box,
	Button,
	CircularProgress,
	CssBaseline,
	Drawer,
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
import { api, cx, getRoute, setRoute } from './modules/utils.js'

const SHELL_MOBILE_QUERY = '(max-width: 1119px)'

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
	const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)')
	const activeTheme = prefersDarkMode ? darkTheme : lightTheme
	const isMobile = useMediaQuery(SHELL_MOBILE_QUERY)

	useEffect(() => {
		document.documentElement.dataset.theme = prefersDarkMode ? 'dark' : 'light'
	}, [prefersDarkMode])

	function notify(message, severity = 'success') {
		setSnack({ open: true, message, severity })
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

						<div className="page-content">
							${route === 'dashboard'
								? html`<${DashboardPage} notify=${notify} />`
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
