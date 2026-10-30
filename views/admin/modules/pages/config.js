import {
	Alert,
	Box,
	Button,
	CircularProgress,
	MenuItem,
	Stack,
	Switch,
	html,
	startTransition,
	useEffect,
	useState
} from '../deps.js'
import { UI } from '../constants.js'
import { api } from '../utils.js'
import { AppTextField, PageHeader, SurfaceCard } from '../components.js'

export function ConfigPage({ notify }) {
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
