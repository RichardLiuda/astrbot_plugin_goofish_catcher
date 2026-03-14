import {
	Button,
	Chip,
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
