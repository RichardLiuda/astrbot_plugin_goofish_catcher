import {
	Box,
	Button,
	Chip,
	CircularProgress,
	Dialog,
	DialogContent,
	DialogTitle,
	LinearProgress,
	MenuItem,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TableRow,
	Typography,
	html,
	startTransition,
	useDeferredValue,
	useEffect,
	useState
} from '../deps.js'
import { UI } from '../constants.js'
import {
	api,
	formatDuration,
	formatMoney,
	formatRatio,
	formatTs,
	statusChipProps,
	toNumberOrNull
} from '../utils.js'
import {
	AppTextField,
	EmptyState,
	PageHeader,
	QueryPreviewPanel,
	SubscriptionDialog,
	SurfaceCard
} from '../components.js'

export function SubscriptionsPage({ notify }) {
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
	const [analyticsTarget, setAnalyticsTarget] = useState(null)

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
			recommend_max_price: toNumberOrNull(form.recommend_max_price),
			drop_abs: toNumberOrNull(form.drop_abs),
			drop_pct: toNumberOrNull(form.drop_pct),
			new_window_sec: toNumberOrNull(form.new_window_sec),
			cooldown_sec: toNumberOrNull(form.cooldown_sec),
			price_min: toNumberOrNull(form.price_min),
			price_max: toNumberOrNull(form.price_max),
			personal_only: Boolean(form.personal_only),
			free_shipping: Boolean(form.free_shipping),
			new_publish_option: String(form.new_publish_option || '').trim(),
			region: String(form.region || '').trim()
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
								recommend_max_price: '',
								drop_abs: 50,
								drop_pct: 0.05,
								new_window_sec: 1800,
								cooldown_sec: 21600,
								personal_only: false,
								free_shipping: false,
								new_publish_option: '',
								region: ''
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
											const ruleSummary = buildRuleSummary(item)
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
															推荐价
															${item.recommend_max_price == null
																? '不限'
																: `≤${formatMoney(
																		item.recommend_max_price
																	)}`}
														<//>
														<${Typography}
															variant="caption"
															color="text.secondary"
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
														${ruleSummary.length
															? html`<div className="chip-row tiny-chip-row">
																	${ruleSummary.map(
																		(label) => html`
																			<${Chip}
																				key=${label}
																				size="small"
																				label=${label}
																				variant="outlined"
																			/>
																		`
																	)}
																</div>`
															: html`<${Typography}
																	variant="caption"
																	color="text.secondary"
																>
																	高级筛选未开启
																<//>`}
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
																	setAnalyticsTarget(
																		item
																	)}
															>
																统计
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
			<${SubscriptionAnalyticsDialog}
				open=${Boolean(analyticsTarget)}
				subscription=${analyticsTarget}
				onClose=${() => setAnalyticsTarget(null)}
				notify=${notify}
			/>
		<//>
	`
}

function buildRuleSummary(item) {
	const parts = []
	if (item.price_min != null || item.price_max != null) {
		const price = []
		if (item.price_min != null) price.push(`≥${formatMoney(item.price_min)}`)
		if (item.price_max != null) price.push(`≤${formatMoney(item.price_max)}`)
		parts.push(`价格 ${price.join(' ')}`)
	}
	if (item.personal_only) parts.push('个人闲置')
	if (item.free_shipping) parts.push('包邮')
	if (item.new_publish_option) parts.push(`新发布 ${item.new_publish_option}`)
	if (item.region) parts.push(`地区 ${item.region}`)
	return parts
}

function SubscriptionAnalyticsDialog({ open, subscription, onClose, notify }) {
	const [data, setData] = useState(null)
	const [loading, setLoading] = useState(false)

	useEffect(() => {
		if (!open || !subscription?.id) {
			setData(null)
			return
		}
		let cancelled = false
		async function load() {
			setLoading(true)
			try {
				const payload = await api(
					`/api/subscriptions/${subscription.id}/analytics`
				)
				if (!cancelled) setData(payload)
			} catch (error) {
				if (!cancelled) notify(error.message, 'error')
			} finally {
				if (!cancelled) setLoading(false)
			}
		}
		load()
		return () => {
			cancelled = true
		}
	}, [open, subscription?.id])

	const stats = data?.stats || {}
	const trends = data?.notification_trends || []
	const recent = data?.recent_recommendations || []

	return html`
		<${Dialog} open=${open} onClose=${onClose} fullWidth=${true} maxWidth="lg">
			<${DialogTitle}>
				${subscription
					? `订阅统计：${subscription.keyword}`
					: '订阅统计'}
			<//>
			<${DialogContent} dividers=${true}>
				${loading && !data
					? html`<${Box} sx=${{ display: 'grid', placeItems: 'center', py: 8 }}>
							<${CircularProgress} />
						<//>`
					: html`
							<${Stack} spacing=${3}>
								<div className="stats-grid compact-stats-grid">
									<${StatMini} label="样本数" value=${stats.sample_count ?? 0} />
									<${StatMini} label="均价" value=${formatMoney(stats.avg_price)} />
									<${StatMini} label="中位数" value=${formatMoney(stats.median_price)} />
									<${StatMini} label="最低价" value=${formatMoney(stats.min_price)} />
									<${StatMini} label="最高价" value=${formatMoney(stats.max_price)} />
								</div>
								<${SurfaceCard}
									title="历史价格走势"
									description="基于 price_history 的轻量 SVG 折线图。"
								>
									<${MiniLineChart}
										points=${data?.price_series || []}
										valueKey="price"
									/>
								<//>
								<${SurfaceCard}
									title="近 30 天通知趋势"
									description="上新与降价通知按天聚合。"
								>
									<${MiniTrendBars} trends=${trends} />
								<//>
								<${SurfaceCard} title="最近推荐商品">
									${recent.length
										? html`<${TableContainer} className="table-wrap compact-table">
												<${Table} size="small">
													<${TableHead}>
														<${TableRow}>
															<${TableCell}>时间<//>
															<${TableCell}>事件<//>
															<${TableCell}>商品<//>
															<${TableCell}>价格<//>
														<//>
													<//>
													<${TableBody}>
														${recent.map((item) => html`
															<${TableRow} key=${`${item.item_id}-${item.sent_at}`}>
																<${TableCell}>${formatTs(item.sent_at)}<//>
																<${TableCell}>${item.event_type}<//>
																<${TableCell}>
																	<${Button}
																		href=${item.url}
																		target="_blank"
																		size="small"
																	>
																		${item.title || item.item_id}
																	<//>
																<//>
																<${TableCell}>${formatMoney(item.price)}<//>
															<//>
														`)}
													<//>
												<//>
											<//>`
										: html`<${EmptyState}
												title="暂无推荐记录"
												description="发送推荐后这里会展示最近商品。"
											/>`}
								<//>
							<//>
						`}
			<//>
		<//>
	`
}

function StatMini({ label, value }) {
	return html`
		<div className="stat-mini">
			<div className="stat-mini-label">${label}</div>
			<div className="stat-mini-value">${value}</div>
		</div>
	`
}

function MiniLineChart({ points, valueKey }) {
	const values = (points || [])
		.map((point) => Number(point[valueKey]))
		.filter((value) => Number.isFinite(value))
	if (!values.length) {
		return html`<${EmptyState}
			title="暂无价格样本"
			description="订阅产生价格历史后会显示走势。"
		/>`
	}
	const width = 720
	const height = 220
	const min = Math.min(...values)
	const max = Math.max(...values)
	const span = max - min || 1
	const d = values
		.map((value, index) => {
			const x = values.length === 1 ? width / 2 : (index / (values.length - 1)) * width
			const y = height - ((value - min) / span) * (height - 24) - 12
			return `${index === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
		})
		.join(' ')
	return html`
		<div className="chart-shell">
			<svg viewBox=${`0 0 ${width} ${height}`} className="analytics-svg">
				<path d=${d} fill="none" stroke="currentColor" strokeWidth="3" />
			</svg>
			<div className="chart-meta">
				最低 ${formatMoney(min)} · 最高 ${formatMoney(max)}
			</div>
		</div>
	`
}

function MiniTrendBars({ trends }) {
	const rows = trends || []
	if (!rows.length) {
		return html`<${EmptyState}
			title="暂无通知趋势"
			description="最近 30 天没有通知记录。"
		/>`
	}
	const max = Math.max(
		1,
		...rows.map((item) => Number(item.new_count || 0) + Number(item.price_drop_count || 0))
	)
	return html`
		<div className="trend-bars">
			${rows.map((item) => {
				const total = Number(item.new_count || 0) + Number(item.price_drop_count || 0)
				return html`
					<div className="trend-bar-row" key=${item.day}>
						<div className="trend-bar-day">${item.day}</div>
						<div className="trend-bar-track">
							<div
								className="trend-bar-fill"
								style=${{ width: `${Math.max(4, (total / max) * 100)}%` }}
							></div>
						</div>
						<div className="trend-bar-value">
							上新 ${item.new_count || 0} / 降价 ${item.price_drop_count || 0}
						</div>
					</div>
				`
			})}
		</div>
	`
}
