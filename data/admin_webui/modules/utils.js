import { NAV_ITEMS } from './constants.js'

export function cx(...names) {
	return names.filter(Boolean).join(' ')
}

export function getRoute() {
	const route = window.location.hash.replace(/^#\/?/, '').trim()
	return NAV_ITEMS.some((item) => item.key === route) ? route : 'dashboard'
}

export function setRoute(route) {
	window.location.hash = `#/${route}`
}

export function formatTs(value) {
	if (!value) {
		return '-'
	}
	return new Date(value * 1000).toLocaleString('zh-CN', { hour12: false })
}

export function formatMoney(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value))) {
		return '-'
	}
	return `¥${Number(value).toFixed(2)}`
}

export function formatRatio(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value))) {
		return '-'
	}
	return `${(Number(value) * 100).toFixed(0)}%`
}

export function formatDuration(value) {
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

export function formatScore(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value))) {
		return '-'
	}
	return `${Number(value).toFixed(1)} 分`
}

export function toNumberOrNull(value) {
	if (value === '' || value === null || value === undefined) {
		return null
	}
	const next = Number(value)
	return Number.isFinite(next) ? next : null
}

export function parseFilterTerms(value) {
	return Array.from(
		new Set(
			String(value || '')
				.split(/[\s,，]+/)
				.map((item) => item.trim().toLowerCase())
				.filter(Boolean)
		)
	)
}

export function shouldHideItemByTerms(item, terms) {
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

export async function api(path, options = {}) {
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

export function statusChipProps(enabled, pausedReason) {
	if (enabled) {
		return { label: '启用中', color: 'success', variant: 'filled' }
	}
	return {
		label: pausedReason || '已暂停',
		color: 'warning',
		variant: 'outlined'
	}
}

export function fetchRunChipProps(status) {
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

export function alertLevelChipProps(level) {
	const normalized = String(level || '').toLowerCase()
	if (normalized.includes('error') || normalized.includes('danger')) {
		return { label: '异常', color: 'error' }
	}
	if (normalized.includes('warn')) {
		return { label: '警告', color: 'warning' }
	}
	return { label: '提示', color: 'primary' }
}

export function riskChipProps(risk) {
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
