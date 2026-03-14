export const NAV_ITEMS = [
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

export const UI = {
	cardPadding: { xs: 2.5, md: 3 },
	pageGap: 3,
	sectionGap: 2.5
}

export const FIELD_CONTROL_SX = {
	'& .MuiInputBase-root': {
		alignItems: 'flex-start',
		borderRadius: '16px',
		border: '1px solid var(--field-border)',
		backgroundColor: 'var(--field-bg)',
		transition:
			'background-color 180ms ease, border-color 180ms ease, box-shadow 180ms ease',
		paddingInline: '14px',
		boxShadow: 'none',
		'&:hover': {
			backgroundColor: 'var(--field-bg-hover)',
			borderColor: 'var(--field-border-hover)'
		},
		'&.Mui-focused': {
			backgroundColor: 'var(--field-bg-focus)',
			borderColor: 'var(--field-border-focus)',
			boxShadow: 'var(--field-focus-ring)'
		},
		'&.Mui-error': {
			borderColor: 'var(--field-error-border)',
			boxShadow: 'var(--field-error-ring)'
		}
	},
	'& .MuiInputBase-input': {
		padding: '15px 0',
		fontSize: '0.95rem',
		lineHeight: 1.55,
		color: 'var(--text)'
	},
	'& .MuiInputBase-input::placeholder': {
		color: 'var(--field-placeholder)',
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
		color: 'var(--field-icon)'
	}
}
