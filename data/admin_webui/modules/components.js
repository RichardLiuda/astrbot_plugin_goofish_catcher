import {
	Alert,
	Box,
	Button,
	Card,
	CardContent,
	Chip,
	Dialog,
	DialogActions,
	DialogContent,
	DialogTitle,
	Stack,
	TextField,
	Typography,
	html,
	useEffect,
	useState
} from './deps.js'
import { FIELD_CONTROL_SX, UI } from './constants.js'
import {
	alertLevelChipProps,
	cx,
	formatMoney,
	formatScore,
	formatTs,
	riskChipProps
} from './utils.js'

export function PageHeader({ title, description, meta, action }) {
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

export function SurfaceCard({
	title,
	description,
	action,
	children,
	className = ''
}) {
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

export function AppTextField({
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

export function StatCard({ label, value, hint, tone = 'primary' }) {
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

export function InfoList({ items }) {
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

export function EmptyState({ title, description }) {
	return html`
		<div className="empty-state">
			<div className="empty-title">${title}</div>
			<div className="empty-description">${description}</div>
		</div>
	`
}

export function AlertFeed({ items }) {
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

export function TrendFeed({ items }) {
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

export function QueryPreviewPanel({ title, preview }) {
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

export function LoginView({ loading, error, onLogin }) {
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

export function SubscriptionDialog({ open, value, onClose, onSubmit }) {
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
