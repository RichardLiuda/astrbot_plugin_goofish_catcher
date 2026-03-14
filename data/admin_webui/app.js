import React, {
	startTransition,
	useDeferredValue,
	useEffect,
	useState
} from 'https://esm.sh/react@18.3.1'
import { createRoot } from 'https://esm.sh/react-dom@18.3.1/client'
import htm from 'https://esm.sh/htm@3.1.1'
import {
	ThemeProvider,
	createTheme
} from 'https://esm.sh/@mui/material@5.16.14/styles?deps=react@18.3.1'
import {
	Alert,
	AppBar,
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	CircularProgress,
	CssBaseline,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	Drawer,
	LinearProgress,
	MenuItem,
	Snackbar,
	Stack,
	Switch,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	TextField,
	Toolbar,
	Typography,
	useMediaQuery
} from 'https://esm.sh/@mui/material@5.16.14?deps=react@18.3.1'

const html = htm.bind(React.createElement)

const NAV_ITEMS = [
	{ key: 'dashboard', label: '总览', description: '关键指标与快速查询' },
	{ key: 'subscriptions', label: '订阅', description: '统一管理监控规则' },
	{ key: 'items', label: '商品', description: '查看商品与关联记录' },
	{
		key: 'runtime',
		label: '运行状态',
		description: '检查 Provider 与抓取情况'
	},
	{ key: 'config', label: '配置', description: '编辑运行时配置' }
]

const UI = {
	cardPadding: { xs: 2.5, md: 3 },
	pageGap: 3,
	sectionGap: 2.5
}

const FIELD_CONTROL_SX = {
	'& .MuiInputBase-root': {
		alignItems: 'flex-start',
		borderRadius: '16px',
		border: '1px solid rgba(167, 145, 102, 0.16)',
		backgroundColor: 'rgba(250, 246, 239, 0.92)',
		transition:
			'background-color 180ms ease, border-color 180ms ease, box-shadow 180ms ease',
		paddingInline: '14px',
		boxShadow: 'none',
		'&:hover': {
			backgroundColor: 'rgba(252, 248, 242, 0.98)',
			borderColor: 'rgba(159, 133, 80, 0.24)'
		},
		'&.Mui-focused': {
			backgroundColor: 'rgba(255, 252, 247, 0.98)',
			borderColor: 'rgba(159, 133, 80, 0.34)',
			boxShadow: '0 0 0 3px rgba(159, 133, 80, 0.08)'
		},
		'&.Mui-error': {
			borderColor: 'rgba(220, 38, 38, 0.28)',
			boxShadow: '0 0 0 3px rgba(220, 38, 38, 0.06)'
		}
	},
	'& .MuiInputBase-input': {
		padding: '15px 0',
		fontSize: '0.95rem',
		lineHeight: 1.55,
		color: '#30261a'
	},
	'& .MuiInputBase-input::placeholder': {
		color: 'rgba(123, 109, 90, 0.72)',
		opacity: 1
	},
	'& .MuiInputBase-inputMultiline': {
		paddingBlock: '15px'
	},
	'& .MuiSelect-select': {
		minHeight: 'unset',
		padding: '15px 26px 15px 0 !important'
	},
	'& .MuiSvgIcon-root': {
		color: '#8b7650'
	}
}

const theme = createTheme({
	palette: {
		mode: 'light',
		primary: { main: '#9f8550' },
		secondary: { main: '#7d6942' },
		success: { main: '#16a34a' },
		warning: { main: '#d97706' },
		error: { main: '#dc2626' },
		background: {
			default: '#f6f1e7',
			paper: '#fdfaf4'
		},
		text: {
			primary: '#30261a',
			secondary: '#7b6d5a'
		}
	},
	shape: {
		borderRadius: 18
	},
	typography: {
		fontFamily:
			"'Avenir Next', 'Segoe UI Variable', 'PingFang SC', 'Noto Sans SC', sans-serif",
		h4: { fontWeight: 720, letterSpacing: '-0.03em' },
		h5: { fontWeight: 700, letterSpacing: '-0.02em' },
		h6: { fontWeight: 700 },
		subtitle1: { fontWeight: 650 },
		subtitle2: { fontWeight: 650 },
		button: { textTransform: 'none', fontWeight: 650 }
	},
	components: {
		MuiCssBaseline: {
			styleOverrides: {
				body: {
					minHeight: '100vh'
				}
			}
		},
		MuiAppBar: {
			styleOverrides: {
				root: {
					borderRadius: 24,
					background: 'rgba(253, 250, 244, 0.9)',
					color: '#30261a',
					border: '1px solid rgba(167, 145, 102, 0.16)',
					boxShadow: '0 12px 30px rgba(112, 93, 60, 0.07)',
					backdropFilter: 'blur(18px)'
				}
			}
		},
		MuiCard: {
			styleOverrides: {
				root: {
					borderRadius: 24,
					background: 'rgba(253, 250, 244, 0.96)',
					border: '1px solid rgba(167, 145, 102, 0.14)',
					boxShadow: '0 16px 40px rgba(112, 93, 60, 0.07)'
				}
			}
		},
		MuiButton: {
			styleOverrides: {
				root: {
					minHeight: 40,
					borderRadius: 14,
					paddingInline: 16
				},
				contained: {
					backgroundColor: '#9f8550',
					boxShadow: 'none',
					'&:hover': {
						backgroundColor: '#8f7648',
						boxShadow: 'none'
					}
				},
				outlined: {
					borderColor: 'rgba(167, 145, 102, 0.28)',
					backgroundColor: 'rgba(250, 246, 237, 0.9)'
				},
				text: {
					color: '#6f5d3e'
				}
			}
		},
		MuiChip: {
			styleOverrides: {
				root: {
					borderRadius: 999,
					fontWeight: 650
				}
			}
		},
		MuiTableCell: {
			styleOverrides: {
				head: {
					color: '#8a7a63',
					fontWeight: 700,
					backgroundColor: 'rgba(249, 244, 233, 0.92)'
				},
				root: {
					borderBottom: '1px solid rgba(231, 222, 203, 0.92)',
					verticalAlign: 'top'
				}
			}
		},
		MuiDialog: {
			styleOverrides: {
				paper: {
					borderRadius: 24,
					border: '1px solid rgba(167, 145, 102, 0.16)',
					boxShadow: '0 24px 64px rgba(112, 93, 60, 0.12)'
				}
			}
		},
		MuiDrawer: {
			styleOverrides: {
				paper: {
					background: 'rgba(252, 249, 242, 0.98)',
					borderLeft: '1px solid rgba(167, 145, 102, 0.14)'
				}
			}
		}
	}
})

function cx(...names) {
	return names.filter(Boolean).join(' ')
}

function getRoute() {
	const route = window.location.hash.replace(/^#\/?/, '').trim()
	return NAV_ITEMS.some((item) => item.key === route) ? route : 'dashboard'
}

function setRoute(route) {
	window.location.hash = `#/${route}`
}

function formatTs(value) {
	if (!value) {
		return '-'
	}
	return new Date(value * 1000).toLocaleString('zh-CN', { hour12: false })
}

function formatMoney(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value))) {
		return '-'
	}
	return `¥${Number(value).toFixed(2)}`
}

function formatRatio(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value))) {
		return '-'
	}
	return `${(Number(value) * 100).toFixed(0)}%`
}

function formatDuration(value) {
	const seconds = Number(value)
	if (!Number.isFinite(seconds) || seconds <= 0) {
		return '-'
	}
	if (seconds < 60) {
		return `${seconds} 秒`
	}
	const units = [
		['天', 86400],
		['小时', 3600],
		['分钟', 60]
	]
	const parts = []
	let rest = seconds
	for (const [label, size] of units) {
		if (rest >= size) {
			const amount = Math.floor(rest / size)
			parts.push(`${amount} ${label}`)
			rest -= amount * size
		}
		if (parts.length === 2) {
			break
		}
	}
	return parts.join(' ')
}

function formatScore(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value))) {
		return '-'
	}
	return `${Number(value).toFixed(1)} 分`
}

function toNumberOrNull(value) {
	if (value === '' || value === null || value === undefined) {
		return null
	}
	const next = Number(value)
	return Number.isFinite(next) ? next : null
}

function parseFilterTerms(value) {
	return Array.from(
		new Set(
			String(value || '')
				.split(/[\s,，]+/)
				.map((item) => item.trim().toLowerCase())
				.filter(Boolean)
		)
	)
}

function shouldHideItemByTerms(item, terms) {
	if (!terms.length) {
		return false
	}
	const haystack = [
		item?.title,
		item?.item_id,
		item?.keyword,
		item?.description,
		item?.desc,
		item?.seller_name,
		item?.seller,
		item?.latest_event_type
	]
		.filter(Boolean)
		.join(' ')
		.toLowerCase()
	return terms.some((term) => haystack.includes(term))
}

async function api(path, options = {}) {
	const config = {
		method: options.method || 'GET',
		credentials: 'include',
		headers: {}
	}
	if (options.body !== undefined) {
		config.headers['Content-Type'] = 'application/json'
		config.body = JSON.stringify(options.body)
	}

	const response = await fetch(path, config)
	const contentType = response.headers.get('content-type') || ''
	const payload = contentType.includes('application/json')
		? await response.json()
		: {}

	if (response.status === 401) {
		const error = new Error('需要重新登录')
		error.code = 'UNAUTHORIZED'
		throw error
	}
	if (!response.ok || payload.ok === false) {
		const error = new Error(
			payload?.error?.message || `请求失败: ${response.status}`
		)
		error.payload = payload
		throw error
	}
	return payload
}

function statusChipProps(enabled, pausedReason) {
	if (enabled) {
		return { label: '启用中', color: 'success', variant: 'filled' }
	}
	return {
		label: pausedReason || '已暂停',
		color: 'warning',
		variant: 'outlined'
	}
}

function fetchRunChipProps(status) {
	const normalized = String(status || '').toUpperCase()
	if (normalized === 'SUCCESS') {
		return { label: '成功', color: 'success', variant: 'filled' }
	}
	if (normalized === 'FAILED') {
		return { label: '失败', color: 'error', variant: 'filled' }
	}
	if (normalized === 'RUNNING') {
		return { label: '运行中', color: 'primary', variant: 'filled' }
	}
	return { label: normalized || '-', color: 'default', variant: 'outlined' }
}

function alertLevelChipProps(level) {
	const normalized = String(level || '').toLowerCase()
	if (normalized.includes('error') || normalized.includes('danger')) {
		return { label: '异常', color: 'error' }
	}
	if (normalized.includes('warn')) {
		return { label: '警告', color: 'warning' }
	}
	return { label: '提示', color: 'primary' }
}

function riskChipProps(risk) {
	const normalized = String(risk || '').toLowerCase()
	if (!normalized || normalized === '-') {
		return { label: '未标记风险', color: 'default', variant: 'outlined' }
	}
	if (normalized.includes('高') || normalized.includes('high')) {
		return { label: risk, color: 'error', variant: 'filled' }
	}
	if (normalized.includes('中') || normalized.includes('medium')) {
		return { label: risk, color: 'warning', variant: 'filled' }
	}
	return { label: risk, color: 'success', variant: 'outlined' }
}

function PageHeader({ title, description, meta, action }) {
	return html`
		<${Stack}
			direction=${{ xs: 'column', md: 'row' }}
			spacing=${2}
			justifyContent="space-between"
			alignItems=${{ xs: 'flex-start', md: 'center' }}
			className="page-header"
		>
			<${Box} sx=${{ flex: 1, minWidth: 0 }}>
				<${Typography} variant="h4">${title}<//>
				${description
					? html`<${Typography}
							variant="body1"
							color="text.secondary"
							sx=${{ mt: 1 }}
						>
							${description}
						<//>`
					: null}
				${meta
					? html`<${Typography}
							variant="caption"
							color="text.secondary"
							sx=${{ mt: 1, display: 'block' }}
						>
							${meta}
						<//>`
					: null}
			<//>
			${action
				? html`<${Box} className="header-actions">${action}<//>`
				: null}
		<//>
	`
}

function SurfaceCard({ title, description, action, children, className = '' }) {
	return html`
		<${Card} elevation=${0} className=${cx('surface-card', className)}>
			<${CardContent} sx=${{ p: UI.cardPadding }}>
				${title || description || action
					? html`
							<${Stack}
								direction=${{ xs: 'column', md: 'row' }}
								spacing=${2}
								justifyContent="space-between"
								alignItems=${{ xs: 'flex-start', md: 'center' }}
							>
								<${Box} sx=${{ flex: 1, minWidth: 0 }}>
									${title
										? html`<${Typography} variant="h6"
												>${title}<//
											>`
										: null}
									${description
										? html`<${Typography}
												variant="body2"
												color="text.secondary"
												sx=${{ mt: title ? 0.75 : 0 }}
											>
												${description}
											<//>`
										: null}
								<//>
								${action ? html`<${Box}>${action}<//>` : null}
							<//>
						`
					: null}
				<${Box} sx=${{ mt: title || description || action ? 2.5 : 0 }}>
					${children}
				<//>
			<//>
		<//>
	`
}

function AppTextField({
	label,
	hint,
	error = '',
	wrapperSx,
	fieldSx,
	fullWidth = true,
	InputProps,
	SelectProps,
	children,
	...props
}) {
	return html`
		<${Box}
			className=${cx('field-block', error && 'has-error')}
			sx=${wrapperSx}
		>
			${label ? html`<div className="field-label">${label}</div>` : null}
			<${TextField}
				...${props}
				fullWidth=${fullWidth}
				variant="standard"
				error=${Boolean(error)}
				label=${undefined}
				helperText=${undefined}
				InputProps=${{ disableUnderline: true, ...(InputProps || {}) }}
				SelectProps=${props.select
					? {
							variant: 'standard',
							disableUnderline: true,
							...(SelectProps || {})
						}
					: SelectProps}
				sx=${[FIELD_CONTROL_SX, fieldSx].filter(Boolean)}
			>
				${children}
			<//>
			${error || hint
				? html`<div className=${cx('field-hint', error && 'is-error')}>
						${error || hint}
					<//>`
				: null}
		<//>
	`
}

function StatCard({ label, value, hint, tone = 'primary' }) {
	const colorMap = {
		primary: 'primary.main',
		success: 'success.main',
		warning: 'warning.main',
		secondary: 'secondary.main'
	}
	return html`
		<${Card}
			elevation=${0}
			className=${cx('surface-card', 'stat-card', `tone-${tone}`)}
		>
			<${CardContent} sx=${{ p: UI.cardPadding }}>
				<${Stack} spacing=${1}>
					<${Typography} variant="body2" color="text.secondary"
						>${label}<//
					>
					<${Typography}
						variant="h5"
						sx=${{ color: colorMap[tone] || 'text.primary' }}
					>
						${value}
					<//>
					<${Typography} variant="body2" color="text.secondary"
						>${hint}<//
					>
				<//>
			<//>
		<//>
	`
}

function InfoList({ items }) {
	const visibleItems = (items || []).filter(
		(item) => item && item.value !== undefined
	)
	if (!visibleItems.length) {
		return html`<div className="empty-state compact-empty">
			暂无可展示信息
		</div>`
	}
	return html`
		<div className="info-list">
			${visibleItems.map(
				(item) => html`
					<div className="info-row" key=${item.label}>
						<span className="info-label">${item.label}</span>
						<span className="info-value">${item.value ?? '-'}</span>
					</div>
				`
			)}
		</div>
	`
}

function EmptyState({ title, description }) {
	return html`
		<div className="empty-state">
			<div className="empty-title">${title}</div>
			<div className="empty-description">${description}</div>
		</div>
	`
}

function AlertFeed({ items }) {
	if (!items?.length) {
		return html`<${EmptyState}
			title="最近没有异常或高优先级告警"
			description="当前运行状态较稳定。"
		/>`
	}
	return html`
		<div className="list-stack">
			${items.map((item) => {
				const chip = alertLevelChipProps(item.level)
				return html`
					<div
						className=${cx('alert-item', `level-${chip.color}`)}
						key=${`${item.keyword}-${item.occurred_at}-${item.message}`}
					>
						<div className="alert-item-head">
							<div className="alert-item-title">
								${item.keyword || '系统'}
							</div>
							<${Chip}
								size="small"
								label=${chip.label}
								color=${chip.color}
							/>
						</div>
						<div className="alert-item-body">
							${item.message || '-'}
						</div>
						<div className="alert-item-time">
							${formatTs(item.occurred_at)}
						</div>
					</div>
				`
			})}
		</div>
	`
}

function TrendFeed({ items }) {
	if (!items?.length) {
		return html`<${EmptyState}
			title="近 7 天没有通知趋势数据"
			description="跑出通知后这里会显示按天统计。"
		/>`
	}
	return html`
		<div className="list-stack">
			${items.map(
				(item) => html`
					<div className="trend-item" key=${item.day}>
						<div>
							<div className="trend-day">${item.day}</div>
							<div className="trend-meta">
								上新 ${item.new_count || 0} 条
							</div>
						</div>
						<${Chip}
							size="small"
							label=${`降价 ${item.price_drop_count || 0} 条`}
							variant="outlined"
						/>
					</div>
				`
			)}
		</div>
	`
}

function QueryPreviewPanel({ title, preview }) {
	if (!preview) {
		return null
	}

	return html`
		<${SurfaceCard}
			title=${title}
			description=${`${preview.keyword} · 抓取 ${preview.page_count} 页`}
			className="query-preview-card"
		>
			<${Stack} spacing=${2.5}>
				<div className="summary-panel">
					<div className="summary-panel-title">分析摘要</div>
					<div className="summary-panel-text">
						${preview.summary || '暂无摘要'}
					</div>
					<div className="chip-row">
						<${Chip}
							size="small"
							label=${preview.used_llm ? 'LLM 推荐' : '规则推荐'}
							color="primary"
						/>
						<${Chip}
							size="small"
							label=${`原始 ${preview.raw_total || 0}`}
							variant="outlined"
						/>
						<${Chip}
							size="small"
							label=${`初筛 ${preview.filtered_total || 0}`}
							variant="outlined"
						/>
						<${Chip}
							size="small"
							label=${preview.filter_mode || '-'}
							variant="outlined"
						/>
					</div>
				</div>

				${preview.fallback_reason
					? html`<${Alert} severity="warning" variant="outlined"
							>${preview.fallback_reason}<//
						>`
					: null}
				${preview.items?.length
					? html`
							<div className="result-grid">
								${preview.items.map((item) => {
									const risk = riskChipProps(item.risk)
									return html`
										<div
											className="result-card"
											key=${item.item_id}
										>
											<div className="result-card-head">
												<div
													className="result-card-title"
												>
													${item.title}
												</div>
												<${Chip}
													size="small"
													label=${formatScore(
														item.score
													)}
													color="primary"
												/>
											</div>
											<div className="result-card-price">
												${formatMoney(item.price)}
											</div>
											<div className="result-card-reason">
												${item.reason || '暂无推荐理由'}
											</div>
											<div className="chip-row">
												<${Chip}
													size="small"
													label=${risk.label}
													color=${risk.color}
													variant=${risk.variant}
												/>
											</div>
											<${Button}
												variant="outlined"
												href=${item.url}
												target="_blank"
											>
												打开商品页
											<//>
										</div>
									`
								})}
							</div>
						`
					: html`<${EmptyState}
							title="本次没有命中推荐商品"
							description="可以尝试放宽关键词或增加抓取页数。"
						/>`}
			<//>
		<//>
	`
}

function LoginView({ loading, error, onLogin }) {
	const [apiKey, setApiKey] = useState('')

	return html`
		<${Box} className="login-shell">
			<${Card} className="login-card" elevation=${0}>
				<${CardContent} sx=${{ p: { xs: 3, md: 4 } }}>
					<${Stack} spacing=${3}>
						<div className="brand-row">
							<div className="brand-mark brand-mark-large">
								<img
									src="/assets/logo.png"
									alt="Goofish Catcher logo"
									className="brand-mark-img"
								/>
							</div>
							<div>
								<${Typography} variant="h5">闲鱼监控管理后台<//>
								<${Typography}
									variant="body2"
									color="text.secondary"
									sx=${{ mt: 0.75 }}
								>
									使用管理员 API Key 登录本地控制台。
								<//>
							</div>
						</div>
						${error
							? html`<${Alert} severity="error" variant="filled"
									>${error}<//
								>`
							: null}
						<${AppTextField}
							label="管理员 API Key"
							type="password"
							value=${apiKey}
							onChange=${(event) => setApiKey(event.target.value)}
							onKeyDown=${(event) => {
								if (event.key === 'Enter' && apiKey.trim()) {
									onLogin(apiKey.trim())
								}
							}}
							hint="输入后台配置的 API Key"
						/>
						<${Button}
							variant="contained"
							size="large"
							disabled=${loading || !apiKey.trim()}
							onClick=${() => onLogin(apiKey.trim())}
						>
							${loading ? '登录中...' : '进入后台'}
						<//>
					<//>
				<//>
			<//>
		<//>
	`
}

function SubscriptionDialog({ open, value, onClose, onSubmit }) {
	const [form, setForm] = useState(value || {})

	useEffect(() => {
		setForm(value || {})
	}, [open, value])

	const fields = [
		['umo', '会话来源 UMO', 'text', '用于标识消息会话或通知出口'],
		['keyword', '关键词', 'text', '订阅关键词，必须填写'],
		['interval_sec', '轮询间隔（秒）', 'number', '建议不要低于 300 秒'],
		['pages', '抓取页数', 'number', '建议 1-2 页'],
		['drop_abs', '绝对降价阈值', 'number', '单位：元'],
		['drop_pct', '相对降价阈值', 'number', '例如 0.05 表示 5%'],
		['new_window_sec', '上新窗口（秒）', 'number', '用于判定上新时间窗'],
		['cooldown_sec', '通知冷却（秒）', 'number', '相同商品事件的通知间隔']
	]

	return html`
		<${Dialog}
			open=${open}
			onClose=${onClose}
			fullWidth=${true}
			maxWidth="md"
		>
			<${DialogTitle}>${value?.id ? '编辑订阅' : '新建订阅'}<//>
			<${DialogContent} dividers=${true}>
				<div className="form-grid">
					${fields.map(
						([key, label, type, helper]) => html`
							<${AppTextField}
								key=${key}
								label=${label}
								type=${type}
								value=${form[key] ?? ''}
								hint=${helper}
								onChange=${(event) =>
									setForm((current) => ({
										...current,
										[key]: event.target.value
									}))}
							/>
						`
					)}
				</div>
			<//>
			<${DialogActions} sx=${{ px: 3, pb: 3, pt: 2 }}>
				<${Button} onClick=${onClose}>取消<//>
				<${Button} variant="contained" onClick=${() => onSubmit(form)}
					>保存<//
				>
			<//>
		<//>
	`
}

function DashboardPage({ notify }) {
	const [overview, setOverview] = useState(null)
	const [query, setQuery] = useState({ keyword: '', pages: 1 })
	const [preview, setPreview] = useState(null)
	const [loading, setLoading] = useState(true)

	async function load() {
		try {
			const payload = await api('/api/overview')
			startTransition(() => setOverview(payload))
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		load()
		const timer = window.setInterval(load, 8000)
		return () => window.clearInterval(timer)
	}, [])

	async function runQuery() {
		try {
			const payload = await api('/api/query', {
				method: 'POST',
				body: {
					keyword: query.keyword,
					pages: Number(query.pages || 1)
				}
			})
			startTransition(() => setPreview(payload.preview))
			notify('临时查询已完成', 'success')
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	if (loading && !overview) {
		return html`
			<${Box} sx=${{ display: 'grid', placeItems: 'center', py: 12 }}>
				<${CircularProgress} />
			<//>
		`
	}

	const health = overview?.provider_health || {}
	const healthItems = [
		{ label: '抓取模式', value: overview?.provider_mode || '-' },
		{
			label: 'Provider 状态',
			value: overview?.provider_available ? '可用' : '异常'
		},
		{
			label: '调度器',
			value: overview?.scheduler_running ? '运行中' : '未运行'
		},
		{
			label: '最近检查',
			value: formatTs(overview?.provider_health_checked_at)
		},
		{
			label: '认证状态',
			value:
				health.auth ||
				(overview?.provider_mode === 'playwright_local'
					? '本地模式'
					: '-')
		},
		{
			label: '登录态文件',
			value:
				health.storage_state === undefined ||
				health.storage_state === null
					? '-'
					: health.storage_state
						? '已就绪'
						: '未找到'
		}
	]

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="控制台总览"
				description="保留运行决策最需要看的状态、告警和快速查询。"
			/>

			<div className="stats-grid">
				<${StatCard}
					label="订阅数量"
					value=${`${overview?.enabled_subscriptions || 0} / ${overview?.total_subscriptions || 0}`}
					hint=${`启用 ${overview?.enabled_subscriptions || 0}，暂停 ${overview?.paused_subscriptions || 0}`}
					tone="primary"
				/>
				<${StatCard}
					label="24 小时成功率"
					value=${`${Number(overview?.success_rate_24h || 0).toFixed(1)}%`}
					hint=${`成功 ${overview?.success_runs_24h || 0} 次，失败 ${overview?.failed_runs_24h || 0} 次`}
					tone="success"
				/>
				<${StatCard}
					label="队列 / 执行中"
					value=${`${overview?.queue_size || 0} / ${overview?.inflight || 0}`}
					hint=${`Worker 数量 ${overview?.workers || 0}`}
					tone="secondary"
				/>
				<${StatCard}
					label="最近告警"
					value=${overview?.recent_alerts?.length || 0}
					hint="展示最近业务与运行异常"
					tone="warning"
				/>
			</div>

			<div className="content-grid two-column">
				<${Stack} spacing=${UI.pageGap}>
					<${SurfaceCard}
						title="临时查询"
						description="不创建订阅，直接执行一次推荐分析。"
					>
						<div className="filter-grid">
							<${AppTextField}
								label="关键词"
								value=${query.keyword}
								onChange=${(event) =>
									setQuery((current) => ({
										...current,
										keyword: event.target.value
									}))}
								hint="输入你想临时分析的关键词"
							/>
							<${AppTextField}
								label="页数"
								type="number"
								value=${query.pages}
								onChange=${(event) =>
									setQuery((current) => ({
										...current,
										pages: event.target.value
									}))}
								wrapperSx=${{ width: { xs: '100%', md: 120 } }}
							/>
							<${Button}
								variant="contained"
								onClick=${runQuery}
								disabled=${!query.keyword.trim()}
							>
								开始分析
							<//>
						</div>

						${preview
							? html`<${Box} sx=${{ mt: 3 }}
									><${QueryPreviewPanel}
										title="查询结果"
										preview=${preview}
								/><//>`
							: null}
					<//>
				<//>
				<${Stack} spacing=${UI.pageGap}>
					<${SurfaceCard}
						title="运行状态"
						description="当前 Provider 与调度器的核心状态。"
					>
						${overview?.provider_error
							? html`<${Alert}
									severity="error"
									variant="outlined"
									sx=${{ mb: 2 }}
								>
									${overview.provider_error}
								<//>`
							: null}
						<${InfoList} items=${healthItems} />
					<//>
					<${SurfaceCard}
						title="最近告警"
						description="帮助快速确认当前是否需要手动介入。"
					>
						<${AlertFeed} items=${overview?.recent_alerts || []} />
					<//>
					<${SurfaceCard}
						title="近 7 天趋势"
						description="按天查看上新与降价通知数量。"
					>
						<${TrendFeed} items=${overview?.trends || []} />
					<//>
				<//>
			</div>
		<//>
	`
}

function SubscriptionsPage({ notify }) {
	const [filters, setFilters] = useState({
		keyword: '',
		status: 'all'
	})
	const [items, setItems] = useState([])
	const [total, setTotal] = useState(0)
	const [loading, setLoading] = useState(true)
	const [dialogOpen, setDialogOpen] = useState(false)
	const [editing, setEditing] = useState(null)
	const [preview, setPreview] = useState(null)

	const deferredKeyword = useDeferredValue(filters.keyword)
	async function load() {
		try {
			const params = new URLSearchParams({
				keyword: deferredKeyword,
				status: filters.status
			})
			const payload = await api(`/api/subscriptions?${params.toString()}`)
			startTransition(() => {
				setItems(payload.items || [])
				setTotal(payload.total || 0)
			})
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		setLoading(true)
		load()
	}, [deferredKeyword, filters.status])

	async function save(form) {
		const body = {
			...form,
			interval_sec: toNumberOrNull(form.interval_sec),
			pages: toNumberOrNull(form.pages),
			drop_abs: toNumberOrNull(form.drop_abs),
			drop_pct: toNumberOrNull(form.drop_pct),
			new_window_sec: toNumberOrNull(form.new_window_sec),
			cooldown_sec: toNumberOrNull(form.cooldown_sec)
		}
		try {
			if (editing?.id) {
				await api(`/api/subscriptions/${editing.id}`, {
					method: 'PATCH',
					body
				})
			} else {
				await api('/api/subscriptions', { method: 'POST', body })
			}
			notify('订阅已保存', 'success')
			setDialogOpen(false)
			setEditing(null)
			load()
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	async function runAction(id, action) {
		try {
			const payload = await api(`/api/subscriptions/${id}/${action}`, {
				method: 'POST'
			})
			if (action === 'check') {
				startTransition(() => setPreview(payload.recommendation))
			}
			notify('操作成功', 'success')
			load()
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	async function remove(id) {
		if (!window.confirm('确认删除这条订阅？')) {
			return
		}
		try {
			await api(`/api/subscriptions/${id}`, { method: 'DELETE' })
			notify('订阅已删除', 'success')
			load()
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="订阅管理"
				description="统一管理关键词、轮询频率和事件阈值。"
				action=${html`
					<${Button}
						variant="contained"
						onClick=${() => {
							setEditing({
								interval_sec: 600,
								pages: 1,
								drop_abs: 50,
								drop_pct: 0.05,
								new_window_sec: 1800,
								cooldown_sec: 21600
							})
							setDialogOpen(true)
						}}
					>
						新建订阅
					<//>
				`}
			/>

			<${SurfaceCard}
				title="筛选"
				description=${`当前共 ${total} 条订阅`}
			>
				<div className="filter-grid">
					<${AppTextField}
						label="关键词"
						value=${filters.keyword}
						onChange=${(event) =>
							setFilters((current) => ({
								...current,
								keyword: event.target.value
							}))}
					/>
					<${AppTextField}
						select=${true}
						label="状态"
						value=${filters.status}
						onChange=${(event) =>
							setFilters((current) => ({
								...current,
								status: event.target.value
							}))}
						wrapperSx=${{ width: { xs: '100%', md: 160 } }}
					>
						<${MenuItem} value="all">全部<//>
						<${MenuItem} value="enabled">启用<//>
						<${MenuItem} value="paused">暂停<//>
					<//>
				</div>
			<//>

			<${SurfaceCard}
				title="订阅列表"
				description="只保留操作所需的关键信息。"
			>
				${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
				${items.length
					? html`
							<${TableContainer}
								className="table-wrap relaxed-table managed-table"
							>
								<${Table} size="small">
									<${TableHead}>
										<${TableRow}>
											<${TableCell} className="table-primary-cell"
												>关键词<//>
											<${TableCell}>状态<//>
											<${TableCell}>频率<//>
											<${TableCell}>规则<//>
											<${TableCell}>最近执行<//>
											<${TableCell}>失败<//>
											<${TableCell}
												align="right"
												className="table-action-cell"
											>
												操作
											<//>
										<//>
									<//>
									<${TableBody}>
										${items.map((item) => {
											const chip = statusChipProps(
												item.enabled,
												item.paused_reason
											)
											return html`
												<${TableRow}
													key=${item.id}
													hover=${true}
												>
													<${TableCell}
														className="table-primary-cell"
													>
														<div className="table-primary-copy">
															<${Typography}
																variant="subtitle2"
																className="table-primary-title"
																>${item.keyword}<//
															>
															<${Typography}
																variant="caption"
																color="text.secondary"
																className="table-primary-meta"
															>
																${`#${item.id} · UMO ${item.umo}`}
															<//>
														</div>
													<//>
													<${TableCell}>
														<${Chip}
															size="small"
															label=${chip.label}
															color=${chip.color}
															variant=${chip.variant}
														/>
													<//>
													<${TableCell}>
														<${Typography}
															variant="body2"
															>${formatDuration(
																item.interval_sec
															)}<//
														>
														<${Typography}
															variant="caption"
															color="text.secondary"
														>
															${item.pages} 页
														<//>
													<//>
													<${TableCell}>
														<${Typography}
															variant="body2"
														>
															降价
															${formatMoney(
																item.drop_abs
															)}
															/
															${formatRatio(
																item.drop_pct
															)}
														<//>
														<${Typography}
															variant="caption"
															color="text.secondary"
														>
															上新
															${formatDuration(
																item.new_window_sec
															)}，冷却
															${formatDuration(
																item.cooldown_sec
															)}
														<//>
													<//>
													<${TableCell}>
														<${Typography}
															variant="body2"
															>${formatTs(
																item.last_run_at
															)}<//
														>
														<${Typography}
															variant="caption"
															color="text.secondary"
														>
															下次
															${formatTs(
																item.next_run_at
															)}
														<//>
													<//>
													<${TableCell}
														>${item.consecutive_failures}<//
													>
													<${TableCell}
														align="right"
														className="table-action-cell"
													>
														<div
															className="table-actions"
														>
															<${Button}
																size="small"
																onClick=${() => {
																	setEditing(
																		item
																	)
																	setDialogOpen(
																		true
																	)
																}}
															>
																编辑
															<//>
															<${Button}
																size="small"
																onClick=${() =>
																	runAction(
																		item.id,
																		'check'
																	)}
															>
																立即检查
															<//>
															<${Button}
																size="small"
																onClick=${() =>
																	runAction(
																		item.id,
																		item.enabled
																			? 'pause'
																			: 'resume'
																	)}
															>
																${item.enabled
																	? '暂停'
																	: '恢复'}
															<//>
															<${Button}
																size="small"
																color="error"
																onClick=${() =>
																	remove(
																		item.id
																	)}
															>
																删除
															<//>
														</div>
													<//>
												<//>
											`
										})}
									<//>
								<//>
							<//>
						`
					: html`<${EmptyState}
							title="没有匹配的订阅"
							description="试试调整筛选条件，或直接新建一条订阅。"
						/>`}
			<//>

			${preview
				? html`<${QueryPreviewPanel}
						title="最近一次检查"
						preview=${preview}
					/>`
				: null}

			<${SubscriptionDialog}
				open=${dialogOpen}
				value=${editing}
				onClose=${() => {
					setDialogOpen(false)
					setEditing(null)
				}}
				onSubmit=${save}
			/>
		<//>
	`
}

function LegacyItemsPage({ notify }) {
	const [search, setSearch] = useState('')
	const [items, setItems] = useState([])
	const [total, setTotal] = useState(0)
	const [loading, setLoading] = useState(true)
	const [detail, setDetail] = useState(null)
	const [drawerOpen, setDrawerOpen] = useState(false)

	const deferredSearch = useDeferredValue(search)

	async function load() {
		try {
			const payload = await api(
				`/api/items?search=${encodeURIComponent(deferredSearch)}`
			)
			startTransition(() => {
				setItems(payload.items || [])
				setTotal(payload.total || 0)
			})
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		setLoading(true)
		load()
	}, [deferredSearch])

	async function openDetail(itemId) {
		setDrawerOpen(true)
		setDetail(null)
		try {
			const payload = await api(`/api/items/${itemId}`)
			startTransition(() => setDetail(payload.item))
		} catch (error) {
			setDrawerOpen(false)
			notify(error.message, 'error')
		}
	}

	const detailItem = detail?.item

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="商品中心"
				description="集中查看商品状态、关联订阅和最近记录。"
			/>

			<${SurfaceCard}
				title="搜索"
				description=${`当前共 ${total} 个商品记录`}
			>
				<${AppTextField}
					label="搜索商品标题或商品 ID"
					value=${search}
					onChange=${(event) => setSearch(event.target.value)}
					hint="支持标题关键词和商品 ID"
				/>
			<//>

			<${SurfaceCard}
				title="商品列表"
				description="保留商品判断最需要的字段。"
			>
				${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
				${items.length
					? html`
							<${TableContainer}
								className="table-wrap relaxed-table managed-table"
							>
								<${Table} size="small">
									<${TableHead}>
										<${TableRow}>
											<${TableCell} className="table-primary-cell"
												>商品<//>
											<${TableCell}>价格<//>
											<${TableCell}>最近发现<//>
											<${TableCell}>订阅数<//>
											<${TableCell}>最新事件<//>
											<${TableCell}
												align="right"
												className="table-action-cell"
											>
												详情
											<//>
										<//>
									<//>
									<${TableBody}>
										${items.map(
											(item) => html`
												<${TableRow}
													key=${item.item_id}
													hover=${true}
												>
													<${TableCell}
														className="table-primary-cell"
													>
														<div className="table-primary-copy">
															<${Typography}
																variant="subtitle2"
																className="table-primary-title"
																>${item.title}<//
															>
															<${Typography}
																variant="caption"
																color="text.secondary"
																className="table-primary-meta"
															>
																${item.item_id}
															<//>
														</div>
													<//>
													<${TableCell}
														>${formatMoney(
															item.price
														)}<//
													>
													<${TableCell}
														>${formatTs(
															item.last_seen_at
														)}<//
													>
													<${TableCell}
														>${item.subscription_count}<//
													>
													<${TableCell}
														>${item.latest_event_type ||
														'-'}<//
													>
													<${TableCell}
														align="right"
														className="table-action-cell"
													>
														<${Button}
															size="small"
															onClick=${() =>
																openDetail(
																	item.item_id
																)}
														>
															查看详情
														<//>
													<//>
												<//>
											`
										)}
									<//>
								<//>
							<//>
						`
					: html`<${EmptyState}
							title="没有匹配的商品"
							description="输入标题关键词或商品 ID 继续筛选。"
						/>`}
			<//>

			<${Drawer}
				anchor="right"
				open=${drawerOpen}
				onClose=${() => setDrawerOpen(false)}
				PaperProps=${{ sx: { width: { xs: '100%', md: 760 } } }}
			>
				<${Box} className="detail-drawer">
					${detail
						? html`
								<${Stack} spacing=${UI.pageGap}>
									<${Box}>
										<${Typography} variant="h5"
											>${detailItem?.title || '-'}<//
										>
										<${Typography}
											variant="body2"
											color="text.secondary"
											sx=${{ mt: 0.75 }}
										>
											${detailItem?.item_id || '-'}
										<//>
									<//>

									<div className="chip-row">
										<${Chip}
											label=${formatMoney(
												detailItem?.price
											)}
											color="primary"
										/>
										<${Chip}
											label=${detailItem?.latest_event_type ||
											'无事件'}
											variant="outlined"
										/>
										<${Button}
											variant="outlined"
											href=${detailItem?.url}
											target="_blank"
										>
											打开商品页
										<//>
									</div>

									<${SurfaceCard} title="基本信息">
										<${InfoList}
											items=${[
												{
													label: '商品 ID',
													value:
														detailItem?.item_id ||
														'-'
												},
												{
													label: '发布时间',
													value: formatTs(
														detailItem?.publish_time
													)
												},
												{
													label: '首次发现',
													value: formatTs(
														detailItem?.first_seen_at
													)
												},
												{
													label: '最近发现',
													value: formatTs(
														detailItem?.last_seen_at
													)
												},
												{
													label: '关联订阅数',
													value: String(
														detailItem?.subscription_count ||
															0
													)
												}
											]}
										/>
									<//>

									<${SurfaceCard}
										title="关联订阅"
										description="展示和这个商品有关的订阅与最后价格。"
									>
										${detail.subscriptions?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}
																		>关键词<//
																	>
																	<${TableCell}
																		>UMO<//
																	>
																	<${TableCell}
																		>状态<//
																	>
																	<${TableCell}
																		>最后价格<//
																	>
																	<${TableCell}
																		>最后关联时间<//
																	>
																<//>
															<//>
															<${TableBody}>
																${detail.subscriptions.map(
																	(item) => {
																		const chip =
																			statusChipProps(
																				item.enabled,
																				item.paused_reason
																			)
																		return html`
																			<${TableRow}
																				key=${item.sub_id}
																			>
																				<${TableCell}
																					>${item.keyword}<//
																				>
																				<${TableCell}
																					>${item.umo}<//
																				>
																				<${TableCell}>
																					<${Chip}
																						size="small"
																						label=${chip.label}
																						color=${chip.color}
																						variant=${chip.variant}
																					/>
																				<//>
																				<${TableCell}
																					>${formatMoney(
																						item.last_price
																					)}<//
																				>
																				<${TableCell}
																					>${formatTs(
																						item.last_seen_at
																					)}<//
																				>
																			<//>
																		`
																	}
																)}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="没有关联订阅"
													description="这个商品还没有被订阅关联记录命中。"
												/>`}
									<//>

									<${SurfaceCard}
										title="价格历史"
										description="默认展示最近 20 条价格记录。"
									>
										${detail.price_history?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}
																		>时间<//
																	>
																	<${TableCell}
																		>价格<//
																	>
																	<${TableCell}
																		>来源<//
																	>
																	<${TableCell}
																		>关键词<//
																	>
																<//>
															<//>
															<${TableBody}>
																${detail.price_history
																	.slice(
																		0,
																		20
																	)
																	.map(
																		(
																			item,
																			index
																		) => html`
																			<${TableRow}
																				key=${`${item.observed_at}-${index}`}
																			>
																				<${TableCell}
																					>${formatTs(
																						item.observed_at
																					)}<//
																				>
																				<${TableCell}
																					>${formatMoney(
																						item.price
																					)}<//
																				>
																				<${TableCell}
																					>${item.source ||
																					'-'}<//
																				>
																				<${TableCell}
																					>${item.keyword ||
																					'-'}<//
																				>
																			<//>
																		`
																	)}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="暂无价格历史"
													description="抓到同一商品的价格变化后会出现在这里。"
												/>`}
									<//>

									<${SurfaceCard}
										title="通知记录"
										description="默认展示最近 15 条通知。"
									>
										${detail.notifications?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}
																		>时间<//
																	>
																	<${TableCell}
																		>事件<//
																	>
																	<${TableCell}
																		>关键词<//
																	>
																	<${TableCell}
																		>UMO<//
																	>
																<//>
															<//>
															<${TableBody}>
																${detail.notifications
																	.slice(
																		0,
																		15
																	)
																	.map(
																		(
																			item,
																			index
																		) => html`
																			<${TableRow}
																				key=${`${item.sent_at}-${index}`}
																			>
																				<${TableCell}
																					>${formatTs(
																						item.sent_at
																					)}<//
																				>
																				<${TableCell}
																					>${item.event_type ||
																					'-'}<//
																				>
																				<${TableCell}
																					>${item.keyword ||
																					'-'}<//
																				>
																				<${TableCell}
																					>${item.umo ||
																					'-'}<//
																				>
																			<//>
																		`
																	)}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="暂无通知记录"
													description="发送过通知后会显示在这里。"
												/>`}
									<//>

									<${SurfaceCard}
										title="抓取记录"
										description="默认展示最近 15 次抓取结果。"
									>
										${detail.fetch_runs?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}
																		>开始时间<//
																	>
																	<${TableCell}
																		>状态<//
																	>
																	<${TableCell}
																		>商品数<//
																	>
																	<${TableCell}
																		>错误<//
																	>
																<//>
															<//>
															<${TableBody}>
																${detail.fetch_runs
																	.slice(
																		0,
																		15
																	)
																	.map(
																		(
																			item
																		) => {
																			const chip =
																				fetchRunChipProps(
																					item.status
																				)
																			return html`
																				<${TableRow}
																					key=${item.id}
																				>
																					<${TableCell}
																						>${formatTs(
																							item.started_at
																						)}<//
																					>
																					<${TableCell}>
																						<${Chip}
																							size="small"
																							label=${chip.label}
																							color=${chip.color}
																							variant=${chip.variant}
																						/>
																					<//>
																					<${TableCell}
																						>${item.items_count}<//
																					>
																					<${TableCell}
																						>${item.err_msg ||
																						'-'}<//
																					>
																				<//>
																			`
																		}
																	)}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="暂无抓取记录"
													description="开始抓取后这里会展示每次执行的结果。"
												/>`}
									<//>
								<//>
							`
						: html`
								<${Box}
									sx=${{
										display: 'grid',
										placeItems: 'center',
										minHeight: 240
									}}
								>
									<${CircularProgress} />
								<//>
							`}
				<//>
			<//>
		<//>
	`
}

function ItemsPage({ notify }) {
	const [filters, setFilters] = useState({
		search: '',
		subId: '',
		view: 'flat',
		blockedTerms: '',
		minPrice: '',
		maxPrice: '',
		sortBy: 'last_seen_at',
		sortOrder: 'desc'
	})
	const [items, setItems] = useState([])
	const [total, setTotal] = useState(0)
	const [loading, setLoading] = useState(true)
	const [detail, setDetail] = useState(null)
	const [drawerOpen, setDrawerOpen] = useState(false)
	const [subscriptionOptions, setSubscriptionOptions] = useState([])

	const deferredSearch = useDeferredValue(filters.search)

	async function loadSubscriptionOptions() {
		try {
			const payload = await api('/api/subscriptions/options')
			startTransition(() => {
				setSubscriptionOptions(payload.items || [])
			})
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	async function load() {
		try {
			const params = new URLSearchParams({
				search: deferredSearch,
				sort_by: filters.sortBy,
				sort_order: filters.sortOrder
			})
			if (filters.subId) {
				params.set('sub_id', filters.subId)
			}
			if (filters.minPrice !== '') {
				params.set('min_price', filters.minPrice)
			}
			if (filters.maxPrice !== '') {
				params.set('max_price', filters.maxPrice)
			}
			const endpoint =
				filters.view === 'by_subscription'
					? '/api/items/by-subscription'
					: '/api/items'
			const payload = await api(`${endpoint}?${params.toString()}`)
			startTransition(() => {
				setItems(payload.items || [])
				setTotal(payload.total || 0)
			})
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		loadSubscriptionOptions()
	}, [])

	useEffect(() => {
		if (
			filters.view === 'by_subscription' &&
			filters.sortBy === 'subscription_count'
		) {
			setFilters((current) => ({
				...current,
				sortBy: 'last_seen_at'
			}))
		}
	}, [filters.view, filters.sortBy])

	useEffect(() => {
		setLoading(true)
		load()
	}, [
		deferredSearch,
		filters.subId,
		filters.view,
		filters.minPrice,
		filters.maxPrice,
		filters.sortBy,
		filters.sortOrder
	])

	async function loadItemDetail(itemId, reset = false) {
		if (reset) {
			setDetail(null)
		}
		const payload = await api(`/api/items/${itemId}`)
		startTransition(() => setDetail(payload.item))
		return payload.item
	}

	async function openDetail(itemId) {
		setDrawerOpen(true)
		try {
			await loadItemDetail(itemId, true)
		} catch (error) {
			setDrawerOpen(false)
			notify(error.message, 'error')
		}
	}

	async function runSubscriptionAction(subId, action, itemId = '') {
		try {
			await api(`/api/subscriptions/${subId}/${action}`, {
				method: 'POST'
			})
			await loadSubscriptionOptions()
			await load()
			if (itemId) {
				await loadItemDetail(itemId)
			}
			notify(
				action === 'check' ? '订阅已执行检查' : '订阅状态已更新',
				'success'
			)
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	function focusSubscription(subId) {
		setFilters((current) => ({
			...current,
			subId: String(subId),
			view: 'by_subscription'
		}))
	}

	const blockedTerms = parseFilterTerms(filters.blockedTerms)
	const visibleItems = items.filter(
		(item) => !shouldHideItemByTerms(item, blockedTerms)
	)
	const groupedItems = []
	if (filters.view === 'by_subscription') {
		const groups = new Map()
		for (const entry of visibleItems) {
			if (!groups.has(entry.sub_id)) {
				const chip = statusChipProps(
					entry.enabled,
					entry.paused_reason
				)
				const group = {
					sub_id: entry.sub_id,
					keyword: entry.keyword,
					umo: entry.umo,
					enabled: entry.enabled,
					paused_reason: entry.paused_reason,
					statusLabel: chip.label,
					statusColor: chip.color,
					statusVariant: chip.variant,
					last_seen_at: entry.last_seen_at,
					items: []
				}
				groups.set(entry.sub_id, group)
				groupedItems.push(group)
			}
			const group = groups.get(entry.sub_id)
			group.items.push(entry)
			group.last_seen_at = Math.max(
				group.last_seen_at || 0,
				entry.last_seen_at || 0
			)
		}
	}

	const detailItem = detail?.item
	const selectedSubscription =
		subscriptionOptions.find(
			(option) => String(option.id) === String(filters.subId || '')
		) || null
	const hiddenByBlockedTerms = items.length - visibleItems.length
	const visibleTotal = visibleItems.length
	const hasCustomFilters = Boolean(
		filters.search.trim() ||
			filters.subId ||
			filters.view !== 'flat' ||
			filters.blockedTerms.trim() ||
			filters.minPrice !== '' ||
			filters.maxPrice !== '' ||
			filters.sortBy !== 'last_seen_at' ||
			filters.sortOrder !== 'desc'
	)

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="商品中心"
				description="集中查看商品、按订阅分类浏览，并在商品上下文里直接处理关联订阅。"
			/>

			<${SurfaceCard}
				title="筛选"
				description=${`当前显示 ${visibleTotal} / ${total} 条${
					filters.view === 'by_subscription'
						? '订阅商品记录'
						: '聚合商品记录'
				}${hiddenByBlockedTerms ? `，已按屏蔽词隐藏 ${hiddenByBlockedTerms} 条` : ''}`}
				action=${hasCustomFilters
					? html`
							<${Button}
								variant="outlined"
								size="small"
								onClick=${() =>
									setFilters({
										search: '',
										subId: '',
										view: 'flat',
										blockedTerms: '',
										minPrice: '',
										maxPrice: '',
										sortBy: 'last_seen_at',
										sortOrder: 'desc'
									})}
							>
								重置
							<//>
						`
					: null}
			>
				<div className="items-filter-layout">
					<div className="items-filter-section">
						<div className="items-filter-section-title">检索与屏蔽</div>
						<div className="filter-grid items-filter-grid">
							<${AppTextField}
								label="搜索商品标题或商品 ID"
								value=${filters.search}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										search: event.target.value
									}))}
								hint="支持标题关键词、商品 ID，也支持在按订阅视图里匹配订阅关键词。"
								wrapperSx=${{ gridColumn: { xs: 'auto', xl: 'span 2' } }}
							/>
							<${AppTextField}
								label="屏蔽词"
								value=${filters.blockedTerms}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										blockedTerms: event.target.value
									}))}
								hint=${hiddenByBlockedTerms
									? `已按屏蔽词隐藏 ${hiddenByBlockedTerms} 条商品，多个词可用空格、逗号或换行分隔。`
									: '命中标题、描述、卖家、订阅关键词时将隐藏，多个词可用空格、逗号或换行分隔。'}
								wrapperSx=${{ gridColumn: { xs: 'auto', xl: 'span 2' } }}
							/>
							<${AppTextField}
								select=${true}
								label="订阅条目"
								value=${filters.subId}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										subId: event.target.value
									}))}
								wrapperSx=${{ gridColumn: { xs: 'auto', lg: 'span 2' } }}
								hint=${selectedSubscription
									? `当前订阅：#${selectedSubscription.id} ${selectedSubscription.keyword}`
									: '可选，按某条订阅聚焦商品。'}
							>
								<${MenuItem} value="">全部订阅<//>
								${subscriptionOptions.map((option) => {
									const suffix = option.enabled ? '' : '（已暂停）'
									return html`
										<${MenuItem}
											key=${option.id}
											value=${String(option.id)}
										>
											${`#${option.id} ${option.keyword}${suffix}`}
										<//>
									`
								})}
							<//>
						</div>
					</div>
					<div className="items-filter-section items-filter-section-secondary">
						<div className="items-filter-section-title">视图与排序</div>
						<div className="filter-grid items-filter-grid items-filter-grid-compact">
							<${AppTextField}
								select=${true}
								label="视图模式"
								value=${filters.view}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										view: event.target.value
									}))}
								hint="聚合商品用于去重查看；按订阅分类用于围绕监控条目管理。"
							>
								<${MenuItem} value="flat">聚合商品<//>
								<${MenuItem} value="by_subscription"
									>按订阅分类<//>
							<//>
							<${AppTextField}
								label="最低价格"
								type="number"
								value=${filters.minPrice}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										minPrice: event.target.value
									}))}
								hint="留空表示不限。"
							/>
							<${AppTextField}
								label="最高价格"
								type="number"
								value=${filters.maxPrice}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										maxPrice: event.target.value
									}))}
								hint="留空表示不限。"
							/>
							<${AppTextField}
								select=${true}
								label="排序字段"
								value=${filters.sortBy}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										sortBy: event.target.value
									}))}
							>
								<${MenuItem} value="last_seen_at">最近发现<//>
								<${MenuItem} value="price">价格<//>
								<${MenuItem} value="publish_time">发布时间<//>
								<${MenuItem} value="title">标题<//>
								${filters.view === 'flat'
									? html`<${MenuItem}
											value="subscription_count"
										>
											订阅数
										<//>`
									: null}
							<//>
							<${AppTextField}
								select=${true}
								label="排序方向"
								value=${filters.sortOrder}
								onChange=${(event) =>
									setFilters((current) => ({
										...current,
										sortOrder: event.target.value
									}))}
							>
								<${MenuItem} value="desc">降序<//>
								<${MenuItem} value="asc">升序<//>
							<//>
						</div>
					</div>
				</div>
			<//>

			${filters.view === 'by_subscription'
				? html`
						<${SurfaceCard}
							title="按订阅分类"
							description="把商品还原到具体订阅条目下，便于逐条管理和快速检查。"
						>
							${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
							${groupedItems.length
								? html`
										<${Stack} spacing=${UI.sectionGap}>
											${groupedItems.map(
												(group) => html`
													<${SurfaceCard}
														key=${group.sub_id}
														title=${`#${group.sub_id} ${group.keyword}`}
														description=${`${group.items.length} 条商品 · 最近发现 ${formatTs(group.last_seen_at)}`}
														action=${html`
															<div className="header-actions">
																<${Chip}
																	size="small"
																	label=${group.statusLabel}
																	color=${group.statusColor}
																	variant=${group.statusVariant}
																/>
																<${Button}
																	size="small"
																	onClick=${() =>
																		runSubscriptionAction(
																			group.sub_id,
																			'check'
																		)}
																>
																	立即检查
																<//>
																<${Button}
																	size="small"
																	onClick=${() =>
																		runSubscriptionAction(
																			group.sub_id,
																			group.enabled
																				? 'pause'
																				: 'resume'
																		)}
																>
																	${group.enabled
																		? '暂停'
																		: '恢复'}
																<//>
																${String(filters.subId || '') !== String(group.sub_id)
																	? html`
																			<${Button}
																				size="small"
																				onClick=${() =>
																					focusSubscription(
																						group.sub_id
																					)}
																			>
																				仅看此订阅
																			<//>
																		`
																	: null}
															</div>
														`}
													>
														<${TableContainer}
															className="table-wrap compact-table managed-table"
														>
															<${Table} size="small">
																<${TableHead}>
																	<${TableRow}>
																		<${TableCell}
																			className="table-primary-cell"
																		>
																			商品
																		<//>
																		<${TableCell}>价格<//>
																		<${TableCell}>最近发现<//>
																		<${TableCell}>最新事件<//>
																		<${TableCell}
																			align="right"
																			className="table-action-cell"
																		>
																			操作
																		<//>
																	<//>
																<//>
																<${TableBody}>
																	${group.items.map(
																		(item) => html`
																			<${TableRow}
																				key=${`${group.sub_id}-${item.item_id}`}
																				hover=${true}
																			>
																				<${TableCell}
																					className="table-primary-cell"
																				>
																					<div className="table-primary-copy item-primary-copy">
																						<${Typography}
																							variant="subtitle2"
																							className="table-primary-title item-primary-title"
																						>
																							${item.title}
																						<//>
																						<${Typography}
																							variant="caption"
																							color="text.secondary"
																							className="table-primary-meta"
																						>
																							${item.item_id}
																						<//>
																					</div>
																				<//>
																				<${TableCell}
																					>${formatMoney(item.price)}<//
																				>
																				<${TableCell}
																					>${formatTs(item.last_seen_at)}<//
																				>
																				<${TableCell}
																					>${item.latest_event_type || '-'}<//
																				>
																				<${TableCell}
																					align="right"
																					className="table-action-cell"
																				>
																					<div className="table-actions">
																						<${Button}
																							size="small"
																							onClick=${() =>
																								openDetail(
																									item.item_id
																								)}
																						>
																							查看详情
																						<//>
																						<${Button}
																							size="small"
																							variant="outlined"
																							href=${item.url}
																							target="_blank"
																						>
																							打开商品
																						<//>
																					</div>
																				<//>
																			<//>
																		`
																	)}
																<//>
															<//>
														<//>
													<//>
												`
											)}
										<//>
									`
								: html`
										<${EmptyState}
											title="没有匹配的订阅商品记录"
											description="可以切换回聚合商品视图，或缩小搜索条件后再试。"
										/>
									`}
						<//>
					`
				: html`
						<${SurfaceCard}
							title="商品列表"
							description="按商品维度聚合去重，便于先快速看盘，再进入明细处理。"
						>
							${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
							${visibleItems.length
								? html`
										<${TableContainer}
											className="table-wrap relaxed-table managed-table"
										>
											<${Table} size="small">
												<${TableHead}>
													<${TableRow}>
														<${TableCell} className="table-primary-cell"
															>商品<//>
														<${TableCell}>价格<//>
														<${TableCell}>最近发现<//>
														<${TableCell}>订阅数<//>
														<${TableCell}>最新事件<//>
														<${TableCell}
															align="right"
															className="table-action-cell"
														>
															详情
														<//>
													<//>
												<//>
												<${TableBody}>
													${visibleItems.map(
														(item) => html`
															<${TableRow}
																key=${item.item_id}
																hover=${true}
															>
																<${TableCell}
																	className="table-primary-cell"
																>
																	<div className="table-primary-copy item-primary-copy">
																		<${Typography}
																			variant="subtitle2"
																			className="table-primary-title item-primary-title"
																		>
																			${item.title}
																		<//>
																		<${Typography}
																			variant="caption"
																			color="text.secondary"
																			className="table-primary-meta"
																		>
																			${item.item_id}
																		<//>
																	</div>
																<//>
																<${TableCell}
																	>${formatMoney(item.price)}<//
																>
																<${TableCell}
																	>${formatTs(item.last_seen_at)}<//
																>
																<${TableCell}
																	>${item.subscription_count}<//
																>
																<${TableCell}
																	>${item.latest_event_type || '-'}<//
																>
																<${TableCell}
																	align="right"
																	className="table-action-cell"
																>
																	<${Button}
																		size="small"
																		onClick=${() =>
																			openDetail(
																				item.item_id
																			)}
																	>
																		查看详情
																	<//>
																<//>
															<//>
														`
													)}
												<//>
											<//>
										<//>
									`
								: html`
										<${EmptyState}
											title="没有匹配的商品"
											description="输入标题关键词、商品 ID，或切换到按订阅分类视图继续查看。"
										/>
									`}
						<//>
					`}

			<${Drawer}
				anchor="right"
				open=${drawerOpen}
				onClose=${() => setDrawerOpen(false)}
				PaperProps=${{ sx: { width: { xs: '100%', md: 760 } } }}
			>
				<${Box} className="detail-drawer">
					${detail
						? html`
								<${Stack} spacing=${UI.pageGap}>
									<${Box}>
										<${Typography} variant="h5"
											>${detailItem?.title || '-'}<//
										>
										<${Typography}
											variant="body2"
											color="text.secondary"
											sx=${{ mt: 0.75 }}
										>
											${detailItem?.item_id || '-'}
										<//>
									<//>

									<div className="chip-row">
										<${Chip}
											label=${formatMoney(detailItem?.price)}
											color="primary"
										/>
										<${Chip}
											label=${detailItem?.latest_event_type || '无事件'}
											variant="outlined"
										/>
										<${Button}
											variant="outlined"
											href=${detailItem?.url}
											target="_blank"
										>
											打开商品页
										<//>
									</div>

									<${SurfaceCard} title="基本信息">
										<${InfoList}
											items=${[
												{
													label: '商品 ID',
													value: detailItem?.item_id || '-'
												},
												{
													label: '发布时间',
													value: formatTs(
														detailItem?.publish_time
													)
												},
												{
													label: '首次发现',
													value: formatTs(
														detailItem?.first_seen_at
													)
												},
												{
													label: '最近发现',
													value: formatTs(
														detailItem?.last_seen_at
													)
												},
												{
													label: '关联订阅数',
													value: String(
														detailItem?.subscription_count ||
															0
													)
												}
											]}
										/>
									<//>

									<${SurfaceCard}
										title="关联订阅"
										description="在商品上下文里直接筛选、检查或暂停关联订阅。"
									>
										${detail.subscriptions?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table managed-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}
																		className="table-primary-cell"
																	>
																		关键词
																	<//>
																	<${TableCell}>状态<//>
																	<${TableCell}>最后价格<//>
																	<${TableCell}
																		>最后关联时间<//
																	>
																	<${TableCell}
																		align="right"
																		className="table-action-cell"
																	>
																		操作
																	<//>
																<//>
															<//>
															<${TableBody}>
																${detail.subscriptions.map(
																	(item) => {
																		const chip =
																			statusChipProps(
																				item.enabled,
																				item.paused_reason
																			)
																		return html`
																			<${TableRow}
																				key=${item.sub_id}
																				hover=${true}
																			>
																				<${TableCell}
																					className="table-primary-cell"
																				>
																					<div className="table-primary-copy">
																						<${Typography}
																							variant="subtitle2"
																							className="table-primary-title"
																						>
																							${item.keyword}
																						<//>
																						<${Typography}
																							variant="caption"
																							color="text.secondary"
																							className="table-primary-meta"
																						>
																							${`#${item.sub_id} · UMO ${item.umo}`}
																						<//>
																					</div>
																				<//>
																				<${TableCell}>
																					<${Chip}
																						size="small"
																						label=${chip.label}
																						color=${chip.color}
																						variant=${chip.variant}
																					/>
																				<//>
																				<${TableCell}
																					>${formatMoney(
																						item.last_price
																					)}<//
																				>
																				<${TableCell}
																					>${formatTs(
																						item.last_seen_at
																					)}<//
																				>
																				<${TableCell}
																					align="right"
																					className="table-action-cell"
																				>
																					<div className="table-actions">
																						<${Button}
																							size="small"
																							onClick=${() =>
																								focusSubscription(
																									item.sub_id
																								)}
																						>
																							按此查看
																						<//>
																						<${Button}
																							size="small"
																							onClick=${() =>
																								runSubscriptionAction(
																									item.sub_id,
																									'check',
																									detailItem?.item_id ||
																										''
																								)}
																						>
																							检查
																						<//>
																						<${Button}
																							size="small"
																							onClick=${() =>
																								runSubscriptionAction(
																									item.sub_id,
																									item.enabled
																										? 'pause'
																										: 'resume',
																									detailItem?.item_id ||
																										''
																								)}
																						>
																							${item.enabled
																								? '暂停'
																								: '恢复'}
																						<//>
																					</div>
																				<//>
																			<//>
																		`
																	}
																)}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="没有关联订阅"
													description="这个商品还没有命中过任何订阅条目。"
												/>`}
									<//>

									<${SurfaceCard}
										title="价格历史"
										description="默认展示最近 20 条价格记录。"
									>
										${detail.price_history?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}>时间<//>
																	<${TableCell}>价格<//>
																	<${TableCell}>来源<//>
																	<${TableCell}>关键词<//>
																<//>
															<//>
															<${TableBody}>
																${detail.price_history
																	.slice(0, 20)
																	.map(
																		(
																			item,
																			index
																		) => html`
																			<${TableRow}
																				key=${`${item.observed_at}-${index}`}
																			>
																				<${TableCell}
																					>${formatTs(
																						item.observed_at
																					)}<//
																				>
																				<${TableCell}
																					>${formatMoney(
																						item.price
																					)}<//
																				>
																				<${TableCell}
																					>${item.source || '-'}<//
																				>
																				<${TableCell}
																					>${item.keyword || '-'}<//
																				>
																			<//>
																		`
																	)}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="暂无价格历史"
													description="抓到同一商品的价格变化后会显示在这里。"
												/>`}
									<//>

									<${SurfaceCard}
										title="通知记录"
										description="默认展示最近 15 条通知。"
									>
										${detail.notifications?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}>时间<//>
																	<${TableCell}>事件<//>
																	<${TableCell}
																		className="table-primary-cell"
																	>
																		关键词
																	<//>
																<//>
															<//>
															<${TableBody}>
																${detail.notifications
																	.slice(0, 15)
																	.map(
																		(
																			item,
																			index
																		) => html`
																			<${TableRow}
																				key=${`${item.sent_at}-${index}`}
																			>
																				<${TableCell}
																					>${formatTs(
																						item.sent_at
																					)}<//
																				>
																				<${TableCell}
																					>${item.event_type || '-'}<//
																				>
																				<${TableCell}
																					className="table-primary-cell"
																				>
																					<div className="table-primary-copy">
																						<${Typography}
																							variant="body2"
																							className="table-primary-title"
																						>
																							${item.keyword || '-'}
																						<//>
																						<${Typography}
																							variant="caption"
																							color="text.secondary"
																							className="table-primary-meta"
																						>
																							${item.umo || '-'}
																						<//>
																					</div>
																				>
																			<//>
																		`
																	)}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="暂无通知记录"
													description="发送过通知后会显示在这里。"
												/>`}
									<//>

									<${SurfaceCard}
										title="抓取记录"
										description="默认展示最近 15 次抓取结果。"
									>
										${detail.fetch_runs?.length
											? html`
													<${TableContainer}
														className="table-wrap compact-table"
													>
														<${Table} size="small">
															<${TableHead}>
																<${TableRow}>
																	<${TableCell}
																		>开始时间<//
																	>
																	<${TableCell}>状态<//>
																	<${TableCell}>商品数<//>
																	<${TableCell}>错误<//>
																<//>
															<//>
															<${TableBody}>
																${detail.fetch_runs
																	.slice(0, 15)
																	.map((item) => {
																		const chip =
																			fetchRunChipProps(
																				item.status
																			)
																		return html`
																			<${TableRow}
																				key=${item.id}
																			>
																				<${TableCell}
																					>${formatTs(
																						item.started_at
																					)}<//
																				>
																				<${TableCell}>
																					<${Chip}
																						size="small"
																						label=${chip.label}
																						color=${chip.color}
																						variant=${chip.variant}
																					/>
																				<//>
																				<${TableCell}
																					>${item.items_count}<//
																				>
																				<${TableCell}
																					>${item.err_msg || '-'}<//
																				>
																			<//>
																		`
																	})}
															<//>
														<//>
													<//>
												`
											: html`<${EmptyState}
													title="暂无抓取记录"
													description="开始抓取后这里会展示每次执行的结果。"
												/>`}
									<//>
								<//>
							`
						: html`
								<${Box}
									sx=${{
										display: 'grid',
										placeItems: 'center',
										minHeight: 240
									}}
								>
									<${CircularProgress} />
								<//>
							`}
				<//>
			<//>
		<//>
	`
}

function RuntimePage({ notify }) {
	const [overview, setOverview] = useState(null)
	const [health, setHealth] = useState(null)
	const [runs, setRuns] = useState([])
	const [loading, setLoading] = useState(true)

	async function load(refresh = false) {
		try {
			const [overviewPayload, healthPayload, runsPayload] =
				await Promise.all([
					api('/api/overview'),
					api(
						`/api/provider/health${refresh ? '?refresh=true' : ''}`
					),
					api('/api/fetch-runs?limit=20')
				])
			startTransition(() => {
				setOverview(overviewPayload)
				setHealth(healthPayload.health)
				setRuns(runsPayload.items || [])
			})
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => {
		load()
		const timer = window.setInterval(() => load(false), 8000)
		return () => window.clearInterval(timer)
	}, [])

	const healthItems = [
		{
			label: 'Provider 模式',
			value: health?.provider || overview?.provider_mode || '-'
		},
		{ label: 'Provider 状态', value: health?.ok ? '可用' : '异常' },
		{ label: '认证状态', value: health?.auth || '-' },
		{
			label: '登录态文件',
			value:
				health?.storage_state === null ||
				health?.storage_state === undefined
					? '-'
					: health.storage_state
						? '已就绪'
						: '未找到'
		},
		{ label: '最近健康检查', value: formatTs(health?.checked_at) },
		{
			label: '队列 / 执行中',
			value: `${overview?.queue_size || 0} / ${overview?.inflight || 0}`
		}
	]

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="运行状态"
				description="关注 Provider 健康、认证状态与最近抓取执行结果。"
				action=${html`
					<${Button} variant="contained" onClick=${() => load(true)}>
						刷新健康检查
					<//>
				`}
			/>

			${loading ? html`<${LinearProgress} />` : null}

			<div className="stats-grid">
				<${StatCard}
					label="调度器"
					value=${overview?.scheduler_running ? '运行中' : '未运行'}
					hint=${`队列 ${overview?.queue_size || 0}，执行中 ${overview?.inflight || 0}`}
					tone="primary"
				/>
				<${StatCard}
					label="Provider"
					value=${overview?.provider_mode || '-'}
					hint=${overview?.provider_error || '当前状态正常'}
					tone="secondary"
				/>
				<${StatCard}
					label="认证状态"
					value=${health?.auth || '-'}
					hint=${health?.storage_state
						? '登录态文件已就绪'
						: '登录态文件待确认'}
					tone="success"
				/>
				<${StatCard}
					label="最近健康检查"
					value=${formatTs(health?.checked_at)}
					hint="默认每 8 秒自动刷新"
					tone="warning"
				/>
			</div>

			<div className="content-grid two-column">
				<${SurfaceCard}
					title="状态摘要"
					description="快速确认当前是否可以正常抓取。"
				>
					${health?.provider_error || overview?.provider_error
						? html`<${Alert}
								severity="error"
								variant="outlined"
								sx=${{ mb: 2 }}
							>
								${health?.provider_error ||
								overview?.provider_error}
							<//>`
						: null}
					<${InfoList} items=${healthItems} />
				<//>

				<${SurfaceCard}
					title="最近抓取记录"
					description="展示最近 20 次抓取执行状态。"
				>
					${runs.length
						? html`
								<${TableContainer}
									className="table-wrap compact-table"
								>
									<${Table} size="small">
										<${TableHead}>
											<${TableRow}>
												<${TableCell}>关键词<//>
												<${TableCell}>状态<//>
												<${TableCell}>开始 / 结束<//>
												<${TableCell}>商品数<//>
												<${TableCell}>错误<//>
											<//>
										<//>
										<${TableBody}>
											${runs.map((item) => {
												const chip = fetchRunChipProps(
													item.status
												)
												return html`
													<${TableRow} key=${item.id}>
														<${TableCell}
															className="table-primary-cell"
														>
															<div className="table-primary-copy">
																<${Typography}
																	variant="body2"
																	className="table-primary-title"
																>
																	${item.keyword}
																<//>
																<${Typography}
																	variant="caption"
																	color="text.secondary"
																	className="table-primary-meta"
																>
																	${item.umo}
																<//>
															</div>
														>
														<${TableCell}>
															<${Chip}
																size="small"
																label=${chip.label}
																color=${chip.color}
																variant=${chip.variant}
															/>
														<//>
														<${TableCell}>
															<${Typography}
																variant="body2"
																>${formatTs(
																	item.started_at
																)}<//
															>
															<${Typography}
																variant="caption"
																color="text.secondary"
															>
																${formatTs(
																	item.finished_at
																)}
															<//>
														<//>
														<${TableCell}
															>${item.items_count}<//
														>
														<${TableCell}
															>${item.err_msg ||
															item.err_type ||
															'-'}<//
														>
													<//>
												`
											})}
										<//>
									<//>
								<//>
							`
						: html`<${EmptyState}
								title="暂无抓取记录"
								description="开始执行订阅后，这里会出现抓取结果。"
							/>`}
				<//>
			</div>
		<//>
	`
}

function ConfigPage({ notify }) {
	const [config, setConfig] = useState(null)
	const [values, setValues] = useState({})
	const [fieldErrors, setFieldErrors] = useState({})
	const [saveMessage, setSaveMessage] = useState('')
	const [reloadResult, setReloadResult] = useState(null)

	async function load() {
		try {
			const payload = await api('/api/config')
			startTransition(() => {
				setConfig(payload.config)
				setValues(payload.config.values || {})
				setFieldErrors({})
			})
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	useEffect(() => {
		load()
	}, [])

	async function save() {
		try {
			const payload = await api('/api/config', {
				method: 'PUT',
				body: { values }
			})
			const changedCount = Object.keys(payload.diff || {}).length
			setSaveMessage(
				changedCount
					? `已保存 ${changedCount} 项配置变更。`
					: '没有检测到配置变化。'
			)
			setFieldErrors({})
			notify('配置已保存', 'success')
		} catch (error) {
			setFieldErrors(error.payload?.field_errors || {})
			notify(error.message, 'error')
		}
	}

	async function reload() {
		try {
			const payload = await api('/api/config/reload', { method: 'POST' })
			setReloadResult(payload)
			notify('运行时配置已重载', 'success')
			load()
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	function renderField(field) {
		const meta = config.schema[field] || {}
		const multiline =
			meta.type === 'list' ||
			meta.type === 'file' ||
			field.includes('prompt') ||
			field === 'remote_headers'
		const isWide = multiline
		const isPassword =
			field.endsWith('api_key') || field === 'remote_api_key'
		const hasOptions =
			Array.isArray(meta.options) && meta.options.length > 0
		const value =
			meta.type === 'list' || meta.type === 'file'
				? Array.isArray(values[field])
					? values[field].join('\n')
					: ''
				: (values[field] ?? '')

		if (meta.type === 'bool') {
			return html`
				<div key=${field} className="field-shell field-shell-wide">
					<div className="switch-row">
						<div>
							<div className="switch-title">
								${meta.description || field}
							</div>
							<div className="switch-hint">
								${fieldErrors[field] || meta.hint || ''}
							</div>
						</div>
						<${Switch}
							checked=${Boolean(values[field])}
							onChange=${(event) =>
								setValues((current) => ({
									...current,
									[field]: event.target.checked
								}))}
						/>
					</div>
				</div>
			`
		}

		return html`
			<${Box}
				key=${field}
				sx=${{ gridColumn: isWide ? '1 / -1' : 'auto' }}
			>
				<${AppTextField}
					select=${hasOptions}
					label=${meta.description || field}
					type=${isPassword
						? 'password'
						: meta.type === 'int' || meta.type === 'float'
							? 'number'
							: 'text'}
					value=${value}
					onChange=${(event) =>
						setValues((current) => ({
							...current,
							[field]:
								meta.type === 'list' || meta.type === 'file'
									? event.target.value
											.split('\n')
											.map((item) => item.trim())
											.filter(Boolean)
									: event.target.value
						}))}
					hint=${meta.hint || ''}
					error=${fieldErrors[field] || ''}
					multiline=${multiline}
					minRows=${multiline ? 4 : 1}
				>
					${hasOptions
						? meta.options.map(
								(option) => html`
									<${MenuItem} key=${option} value=${option}
										>${option}<//
									>
								`
							)
						: null}
				<//>
			<//>
		`
	}

	if (!config) {
		return html`
			<${Box} sx=${{ display: 'grid', placeItems: 'center', py: 12 }}>
				<${CircularProgress} />
			<//>
		`
	}

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="运行时配置"
				description="直接编辑覆盖层配置并在运行时重载。"
				meta=${`覆盖层文件：${config.overlay_path}`}
				action=${html`
					<div className="chip-row">
						<${Button} variant="outlined" onClick=${load}>刷新<//>
						<${Button} variant="contained" onClick=${save}>保存<//>
						<${Button}
							variant="contained"
							color="secondary"
							onClick=${reload}
							>应用重载<//
						>
					</div>
				`}
			/>

			${saveMessage
				? html`<${Alert} severity="success" variant="outlined"
						>${saveMessage}<//
					>`
				: null}
			${reloadResult
				? html`
						<${Alert}
							severity=${reloadResult.provider_error
								? 'warning'
								: 'success'}
							variant="outlined"
						>
							${reloadResult.admin_server_restart_required
								? '管理后台监听地址相关配置已修改，需要重启插件后生效。'
								: '运行时配置已生效。'}
							${reloadResult.provider_error
								? ` 当前 Provider 状态异常：${reloadResult.provider_error}`
								: ''}
						<//>
					`
				: null}

			<div className="config-groups">
				${config.groups.map(
					(group) => html`
						<${SurfaceCard} key=${group.id} title=${group.title}>
							<div className="form-grid">
								${group.fields.map((field) =>
									renderField(field)
								)}
							</div>
						<//>
					`
				)}
			</div>
		<//>
	`
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
	const isMobile = useMediaQuery(theme.breakpoints.down('lg'))

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
			<${ThemeProvider} theme=${theme}>
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
			<${ThemeProvider} theme=${theme}>
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
		<${ThemeProvider} theme=${theme}>
			<${CssBaseline} />
			<div className="app-shell">
				${isMobile
					? html`
							<${Drawer}
								open=${drawerOpen}
								onClose=${() => setDrawerOpen(false)}
								PaperProps=${{ sx: { width: 320, p: 2 } }}
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
							sx=${{ top: 0 }}
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
													setDrawerOpen(true)}
												sx=${{ mr: 1.5 }}
											>
												导航
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
