import {
	Box,
	Button,
	Checkbox,
	Chip,
	Dialog,
	DialogActions,
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
	Tooltip,
	Typography,
	html,
	startTransition,
	useCallback,
	useDeferredValue,
	useEffect,
	useMediaQuery,
	useState
} from '../deps.js'
import { UI } from '../constants.js'
import {
	api,
	formatMoney,
	formatTs,
	parseFilterTerms,
	shouldHideItemByTerms,
	statusChipProps
} from '../utils.js'
import { AppTextField, EmptyState, PageHeader, SurfaceCard } from '../components.js'
import { ItemDetailContent, ItemDetailDrawer } from './items-detail-drawer.js'

// ── 删除确认对话框 ──────────────────────────────────────────────────────────
function DeleteConfirmDialog({ open, count, onConfirm, onCancel, loading }) {
	return html`
		<${Dialog} open=${open} onClose=${onCancel} maxWidth="xs" fullWidth=${true}>
			<${DialogTitle}>确认删除<//>
			<${DialogContent}>
				<${Typography}>
					即将删除 <strong>${count}</strong> 条商品记录（包含对应的价格历史），此操作不可撤销，确定继续？
				<//>
			<//>
			<${DialogActions}>
				<${Button} onClick=${onCancel} disabled=${loading}>取消<//>
				<${Button}
					onClick=${onConfirm}
					color="error"
					variant="contained"
					disabled=${loading}
				>
					${loading ? '删除中…' : '确认删除'}
				<//>
			<//>
		<//>
	`
}

// ── 工具栏：多选状态下显示的批量操作区 ──────────────────────────────────────
function SelectionToolbar({ selectedCount, totalCount, onSelectAll, onClearAll, onDelete }) {
	const allSelected = selectedCount > 0 && selectedCount === totalCount
	const someSelected = selectedCount > 0 && selectedCount < totalCount
	return html`
		<div className="selection-toolbar">
			<${Checkbox}
				indeterminate=${someSelected}
				checked=${allSelected}
				onChange=${allSelected || someSelected ? onClearAll : onSelectAll}
				size="small"
			/>
			<${Typography} variant="body2" sx=${{ mx: 1, minWidth: 80 }}>
				${selectedCount > 0 ? `已选 ${selectedCount} 条` : `共 ${totalCount} 条`}
			<//>
			${selectedCount > 0
				? html`
						<${Button}
							size="small"
							color="error"
							variant="outlined"
							onClick=${onDelete}
							sx=${{ ml: 1 }}
						>
							删除所选 (${selectedCount})
						<//>
						<${Button}
							size="small"
							variant="text"
							onClick=${onClearAll}
							sx=${{ ml: 0.5 }}
						>
							取消选择
						<//>
					`
				: null}
		</div>
	`
}

export function ItemsPage({ notify }) {
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
	// 多选状态
	const [selected, setSelected] = useState(new Set())
	const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
	const [deleteLoading, setDeleteLoading] = useState(false)

	const isNarrowScreen = useMediaQuery('(max-width: 720px)')
	const deferredSearch = useDeferredValue(filters.search)

	// 切换筛选条件时清空选择
	const clearSelection = useCallback(() => setSelected(new Set()), [])

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
			if (filters.subId) params.set('sub_id', filters.subId)
			if (filters.minPrice !== '') params.set('min_price', filters.minPrice)
			if (filters.maxPrice !== '') params.set('max_price', filters.maxPrice)
			const endpoint =
				filters.view === 'by_subscription'
					? '/api/items/by-subscription'
					: '/api/items'
			const payload = await api(`${endpoint}?${params.toString()}`)
			startTransition(() => {
				setItems(payload.items || [])
				setTotal(payload.total || 0)
				clearSelection()
			})
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => { loadSubscriptionOptions() }, [])

	useEffect(() => {
		if (filters.view === 'by_subscription' && filters.sortBy === 'subscription_count') {
			setFilters((c) => ({ ...c, sortBy: 'last_seen_at' }))
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
		if (reset) setDetail(null)
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
			await api(`/api/subscriptions/${subId}/${action}`, { method: 'POST' })
			await loadSubscriptionOptions()
			await load()
			if (itemId) await loadItemDetail(itemId)
			notify(action === 'check' ? '订阅已执行检查' : '订阅状态已更新', 'success')
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	function focusSubscription(subId) {
		setDrawerOpen(false)
		setFilters((c) => ({ ...c, subId: String(subId), view: 'by_subscription' }))
	}

	// ── 删除逻辑 ────────────────────────────────────────────────────────────
	async function handleDeleteSelected() {
		if (selected.size === 0) return
		setDeleteLoading(true)
		try {
			const subIdNum = filters.subId ? parseInt(filters.subId, 10) : 0
			await api('/api/items', {
				method: 'DELETE',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					item_ids: Array.from(selected),
					sub_id: subIdNum
				})
			})
			notify(`已删除 ${selected.size} 条商品记录`, 'success')
			setDeleteDialogOpen(false)
			clearSelection()
			await load()
		} catch (error) {
			notify(error.message, 'error')
		} finally {
			setDeleteLoading(false)
		}
	}

	async function handleDeleteOne(itemId) {
		try {
			const subIdNum = filters.subId ? parseInt(filters.subId, 10) : 0
			await api('/api/items', {
				method: 'DELETE',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ item_ids: [itemId], sub_id: subIdNum })
			})
			notify('商品记录已删除', 'success')
			if (drawerOpen) setDrawerOpen(false)
			clearSelection()
			await load()
		} catch (error) {
			notify(error.message, 'error')
		}
	}

	// ── 多选辅助 ─────────────────────────────────────────────────────────────
	function toggleItem(itemId) {
		setSelected((prev) => {
			const next = new Set(prev)
			if (next.has(itemId)) next.delete(itemId)
			else next.add(itemId)
			return next
		})
	}

	// ── 过滤 / 分组 ──────────────────────────────────────────────────────────
	const blockedTerms = parseFilterTerms(filters.blockedTerms)
	const visibleItems = items.filter((item) => !shouldHideItemByTerms(item, blockedTerms))
	const groupedItems = []
	if (filters.view === 'by_subscription') {
		const groups = new Map()
		for (const entry of visibleItems) {
			if (!groups.has(entry.sub_id)) {
				const chip = statusChipProps(entry.enabled, entry.paused_reason)
				groups.set(entry.sub_id, {
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
				})
				groupedItems.push(groups.get(entry.sub_id))
			}
			const group = groups.get(entry.sub_id)
			group.items.push(entry)
			group.last_seen_at = Math.max(group.last_seen_at || 0, entry.last_seen_at || 0)
		}
	}

	const selectedSubscription =
		subscriptionOptions.find((o) => String(o.id) === String(filters.subId || '')) || null
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

	// 全选只作用于当前可见列表
	const visibleItemIds = visibleItems.map((i) => i.item_id)
	const allVisibleSelected =
		visibleItemIds.length > 0 && visibleItemIds.every((id) => selected.has(id))
	const someVisibleSelected = visibleItemIds.some((id) => selected.has(id)) && !allVisibleSelected

	function selectAll() {
		setSelected((prev) => {
			const next = new Set(prev)
			visibleItemIds.forEach((id) => next.add(id))
			return next
		})
	}

	// 窄屏单页详情
	if (isNarrowScreen && drawerOpen) {
		return html`
			<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
				<${PageHeader}
					title="商品详情"
					description="窄屏下切换为单页详情视图，返回后继续保留当前筛选条件。"
					action=${html`
						<${Button} variant="outlined" onClick=${() => setDrawerOpen(false)}>
							返回列表
						<//>
					`}
				/>
				<${ItemDetailContent}
					detail=${detail}
					onFocusSubscription=${focusSubscription}
					onRunSubscriptionAction=${runSubscriptionAction}
					onDelete=${handleDeleteOne}
				/>
			<//>
		`
	}

	return html`
		<${Stack} spacing=${UI.pageGap} className="page-enter page-stack">
			<${PageHeader}
				title="商品记录"
				description="查看、搜索、过滤已抓取的商品，支持多选批量删除。"
			/>

			${/* ── 筛选卡片 ── */ ''}
			<${SurfaceCard}
				title="搜索与过滤"
				description=${`当前显示 ${visibleTotal} / ${total} 条${
					filters.view === 'by_subscription' ? '（按订阅分类）' : '（聚合去重）'
				}${hiddenByBlockedTerms ? `，屏蔽词已隐藏 ${hiddenByBlockedTerms} 条` : ''}`}
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
								清除筛选
							<//>
						`
					: null}
			>
				<div className="items-filter-layout">
					<div className="items-filter-section">
						<div className="items-filter-section-title">搜索 / 屏蔽</div>
						<div className="filter-grid items-filter-grid">
							<${AppTextField}
								label="搜索商品标题或商品 ID"
								value=${filters.search}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, search: e.target.value }))}
								hint="支持标题关键词、商品 ID；在「按订阅」视图下也可匹配订阅关键词。"
								wrapperSx=${{ gridColumn: { xs: 'auto', xl: 'span 2' } }}
							/>
							<${AppTextField}
								label="屏蔽词（不删除，仅隐藏）"
								value=${filters.blockedTerms}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, blockedTerms: e.target.value }))}
								hint=${hiddenByBlockedTerms
									? `当前已隐藏 ${hiddenByBlockedTerms} 条，多个词可用空格、逗号或换行分隔。`
									: '命中标题时仅隐藏显示，不影响数据库，多个词可用空格/逗号/换行分隔。'}
								wrapperSx=${{ gridColumn: { xs: 'auto', xl: 'span 2' } }}
							/>
							<${AppTextField}
								select=${true}
								label="订阅条目"
								value=${filters.subId}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, subId: e.target.value }))}
								wrapperSx=${{ gridColumn: { xs: 'auto', lg: 'span 2' } }}
								hint=${selectedSubscription
									? `当前：#${selectedSubscription.id} ${selectedSubscription.keyword}`
									: '可选，只看某条订阅的商品。'}
							>
								<${MenuItem} value="">全部订阅<//>
								${subscriptionOptions.map((o) => {
									const suffix = o.enabled ? '' : '（已暂停）'
									return html`
										<${MenuItem} key=${o.id} value=${String(o.id)}>
											${`#${o.id} ${o.keyword}${suffix}`}
										<//>
									`
								})}
							<//>
						</div>
					</div>
					<div className="items-filter-section items-filter-section-secondary">
						<div className="items-filter-section-title">视图 / 排序</div>
						<div className="filter-grid items-filter-grid items-filter-grid-compact">
							<${AppTextField}
								select=${true}
								label="视图模式"
								value=${filters.view}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, view: e.target.value }))}
								hint="聚合模式按商品去重；按订阅模式把商品归到各条订阅下管理。"
							>
								<${MenuItem} value="flat">聚合去重<//>
								<${MenuItem} value="by_subscription">按订阅分类<//>
							<//>
							<${AppTextField}
								label="最低价格"
								type="number"
								value=${filters.minPrice}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, minPrice: e.target.value }))}
								hint="留空不限。"
							/>
							<${AppTextField}
								label="最高价格"
								type="number"
								value=${filters.maxPrice}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, maxPrice: e.target.value }))}
								hint="留空不限。"
							/>
							<${AppTextField}
								select=${true}
								label="排序字段"
								value=${filters.sortBy}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, sortBy: e.target.value }))}
							>
								<${MenuItem} value="last_seen_at">最近发现<//>
								<${MenuItem} value="price">价格<//>
								<${MenuItem} value="publish_time">发布时间<//>
								<${MenuItem} value="title">标题<//>
								${filters.view === 'flat'
									? html`<${MenuItem} value="subscription_count">订阅数<//>`
									: null}
							<//>
							<${AppTextField}
								select=${true}
								label="排序方向"
								value=${filters.sortOrder}
								onChange=${(e) =>
									setFilters((c) => ({ ...c, sortOrder: e.target.value }))}
							>
								<${MenuItem} value="desc">降序<//>
								<${MenuItem} value="asc">升序<//>
							<//>
						</div>
					</div>
				</div>
			<//>

			${/* ── 按订阅分类视图 ── */ ''}
			${filters.view === 'by_subscription'
				? html`
						<${SurfaceCard}
							title="按订阅分类"
							description="把商品还原到各条订阅下，便于逐条管理。"
						>
							${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}
							${groupedItems.length
								? html`
										<${Stack} spacing=${UI.sectionGap}>
											${groupedItems.map(
												(group) => html`
													<${SurfaceCard}
														key=${group.sub_id}
														title=${`#${group.sub_id} · ${group.keyword}`}
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
																	${group.enabled ? '暂停' : '恢复'}
																<//>
																${String(filters.subId || '') !==
																String(group.sub_id)
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
																			padding="checkbox"
																			sx=${{ width: 40 }}
																		>
																			<${Tooltip}
																				title="全选本组"
																			>
																				<${Checkbox}
																					size="small"
																					indeterminate=${group.items.some(
																						(i) =>
																							selected.has(
																								i.item_id
																							)
																					) &&
																					!group.items.every(
																						(i) =>
																							selected.has(
																								i.item_id
																							)
																					)}
																					checked=${group.items.every(
																						(i) =>
																							selected.has(
																								i.item_id
																							)
																					)}
																					onChange=${() => {
																						const allSel =
																							group.items.every(
																								(i) =>
																									selected.has(
																										i.item_id
																									)
																							)
																						setSelected(
																							(prev) => {
																								const next =
																									new Set(
																										prev
																									)
																								group.items.forEach(
																									(i) => {
																										if (
																											allSel
																										)
																											next.delete(
																												i.item_id
																											)
																										else
																											next.add(
																												i.item_id
																											)
																									}
																								)
																								return next
																							}
																						)
																					}}
																				/>
																			<//>
																		<//>
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
																				selected=${selected.has(
																					item.item_id
																				)}
																			>
																				<${TableCell}
																					padding="checkbox"
																				>
																					<${Checkbox}
																						size="small"
																						checked=${selected.has(
																							item.item_id
																						)}
																						onChange=${() =>
																							toggleItem(
																								item.item_id
																							)}
																					/>
																				<//>
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
																				<${TableCell}>
																					${formatMoney(
																						item.price
																					)}
																				<//>
																				<${TableCell}>
																					${formatTs(
																						item.last_seen_at
																					)}
																				<//>
																				<${TableCell}>
																					${item.latest_event_type ||
																					'-'}
																				<//>
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
																							详情
																						<//>
																						<${Button}
																							size="small"
																							variant="outlined"
																							href=${item.url}
																							target="_blank"
																						>
																							打开
																						<//>
																						<${Button}
																							size="small"
																							color="error"
																							onClick=${() =>
																								handleDeleteOne(
																									item.item_id
																								)}
																						>
																							删除
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
											title="没有匹配的订阅商品"
											description="可以切换回「聚合去重」视图，或缩小搜索条件后再试。"
										/>
									`}

							${/* 按订阅视图的批量删除工具栏 */ ''}
							${selected.size > 0
								? html`
										<${SelectionToolbar}
											selectedCount=${selected.size}
											totalCount=${visibleTotal}
											onSelectAll=${selectAll}
											onClearAll=${clearSelection}
											onDelete=${() => setDeleteDialogOpen(true)}
										/>
									`
								: null}
						<//>
					`
				: html`
						${/* ── 聚合去重视图 ── */ ''}
						<${SurfaceCard}
							title="商品列表"
							description="按商品去重聚合，快速浏览当前库存的所有商品。"
						>
							${loading ? html`<${LinearProgress} sx=${{ mb: 2 }} />` : null}

							${/* 多选工具栏始终显示在列表上方 */ ''}
							<${SelectionToolbar}
								selectedCount=${selected.size}
								totalCount=${visibleTotal}
								onSelectAll=${selectAll}
								onClearAll=${clearSelection}
								onDelete=${() => setDeleteDialogOpen(true)}
							/>

							${visibleItems.length
								? html`
										<${TableContainer}
											className="table-wrap relaxed-table managed-table"
										>
											<${Table} size="small">
												<${TableHead}>
													<${TableRow}>
														<${TableCell}
															padding="checkbox"
															sx=${{ width: 40 }}
														>
															<${Tooltip} title="全选当前列表">
																<${Checkbox}
																	size="small"
																	indeterminate=${someVisibleSelected}
																	checked=${allVisibleSelected}
																	onChange=${allVisibleSelected
																		? clearSelection
																		: selectAll}
																/>
															<//>
														<//>
														<${TableCell} className="table-primary-cell">
															商品
														<//>
														<${TableCell}>价格<//>
														<${TableCell}>最近发现<//>
														<${TableCell}>订阅数<//>
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
													${visibleItems.map(
														(item) => html`
															<${TableRow}
																key=${item.item_id}
																hover=${true}
																selected=${selected.has(item.item_id)}
															>
																<${TableCell} padding="checkbox">
																	<${Checkbox}
																		size="small"
																		checked=${selected.has(
																			item.item_id
																		)}
																		onChange=${() =>
																			toggleItem(item.item_id)}
																	/>
																<//>
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
																<${TableCell}>
																	${formatMoney(item.price)}
																<//>
																<${TableCell}>
																	${formatTs(item.last_seen_at)}
																<//>
																<${TableCell}>
																	${item.subscription_count}
																<//>
																<${TableCell}>
																	${item.latest_event_type || '-'}
																<//>
																<${TableCell}
																	align="right"
																	className="table-action-cell"
																>
																	<div className="table-actions">
																		<${Button}
																			size="small"
																			onClick=${() =>
																				openDetail(item.item_id)}
																		>
																			详情
																		<//>
																		<${Button}
																			size="small"
																			color="error"
																			onClick=${() =>
																				handleDeleteOne(
																					item.item_id
																				)}
																		>
																			删除
																		<//>
																	</div>
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
											description="输入标题关键词或商品 ID 搜索，或切换到「按订阅分类」视图。"
										/>
									`}
						<//>
					`}

			${/* ── 删除确认对话框 ── */ ''}
			<${DeleteConfirmDialog}
				open=${deleteDialogOpen}
				count=${selected.size}
				loading=${deleteLoading}
				onConfirm=${handleDeleteSelected}
				onCancel=${() => setDeleteDialogOpen(false)}
			/>

			${/* ── 详情抽屉（宽屏） ── */ ''}
			${!isNarrowScreen
				? html`
						<${ItemDetailDrawer}
							open=${drawerOpen}
							detail=${detail}
							onClose=${() => setDrawerOpen(false)}
							onFocusSubscription=${focusSubscription}
							onRunSubscriptionAction=${runSubscriptionAction}
							onDelete=${handleDeleteOne}
						/>
					`
				: null}
		<//>
	`
}
