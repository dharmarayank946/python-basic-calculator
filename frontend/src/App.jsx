import React, { useState, useEffect, useCallback } from 'react'

const API_BASE = (import.meta.env.VITE_API_URL || 'https://python-basic-calculator-1.onrender.com').replace(/\/+$/, '')

export default function App() {
  const [expression, setExpression] = useState('')
  const [display, setDisplay] = useState('0')
  const [mode, setMode] = useState('standard') // 'standard' | 'scientific'
  const [showHistory, setShowHistory] = useState(false)
  const [history, setHistory] = useState([])
  const [isNewCalculation, setIsNewCalculation] = useState(true)
  const [toast, setToast] = useState(null)

  const showToastMsg = (msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 2000)
  }

  // Safe client-side math evaluator with API server fallback
  const evaluateMath = useCallback(async (expr) => {
    if (!expr || expr === '0') return '0'

    // Clean display symbols
    const cleanExpr = expr
      .replace(/×/g, '*')
      .replace(/÷/g, '/')
      .replace(/−/g, '-')
      .replace(/\^/g, '**')

    // Try API if configured
    if (API_BASE) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/calculator/evaluate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ expression: cleanExpr })
        })
        const data = await res.json()
        if (data.success) {
          return data.formatted
        } else {
          return data.error || 'Error'
        }
      } catch (err) {
        console.warn('API fetch failed, falling back to client evaluation', err)
      }
    }

    // Safe client-side evaluation without eval()
    try {
      // Whitelist characters to prevent arbitrary code
      if (!/^[\d\s+\-*/().%^eE]+$/.test(cleanExpr)) {
        return 'Invalid input'
      }
      // Use Function constructor with math scope, avoiding global access
      const sanitized = cleanExpr.replace(/(\d+)%/g, '($1/100)')
      const fn = new Function(`'use strict'; return (${sanitized});`)
      const res = fn()
      if (typeof res !== 'number' || isNaN(res)) return 'Error'
      if (!isFinite(res)) return 'Cannot divide by zero'
      return Number(res.toFixed(10)).toString()
    } catch {
      return 'Malformed expression'
    }
  }, [])

  const handleDigit = (digit) => {
    if (isNewCalculation || display === '0' || display === 'Error') {
      setDisplay(digit)
      setIsNewCalculation(false)
    } else {
      setDisplay(display + digit)
    }
  }

  const handleOperator = (op) => {
    setIsNewCalculation(false)
    if (display === 'Error') {
      setDisplay('0')
      return
    }
    const current = expression ? `${expression} ${display} ${op}` : `${display} ${op}`
    setExpression(current)
    setDisplay('0')
  }

  const handleEquals = async () => {
    const fullExpr = expression ? `${expression} ${display}` : display
    const res = await evaluateMath(fullExpr)
    
    if (res !== 'Error' && !res.includes('Cannot') && !res.includes('Invalid')) {
      const item = { expr: fullExpr, res, time: new Date().toLocaleTimeString() }
      setHistory(prev => [item, ...prev].slice(0, 30))
    }
    setDisplay(res)
    setExpression('')
    setIsNewCalculation(true)
  }

  const handleClear = () => {
    setDisplay('0')
    setExpression('')
    setIsNewCalculation(true)
  }

  const handleBackspace = () => {
    if (isNewCalculation || display === 'Error' || display.length <= 1) {
      setDisplay('0')
      setIsNewCalculation(true)
    } else {
      setDisplay(display.slice(0, -1))
    }
  }

  const handleScientific = async (op) => {
    const val = parseFloat(display)
    if (isNaN(val)) return

    // Call Render backend API if available
    if (API_BASE) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/calculator/function`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ operation: op, value: val })
        })
        const data = await res.json()
        if (data.success) {
          setDisplay(data.formatted)
          setIsNewCalculation(true)
          return
        } else if (data.error) {
          setDisplay(data.error)
          setIsNewCalculation(true)
          return
        }
      } catch (err) {
        console.warn('Function API failed, using offline fallback', err)
      }
    }

    // Offline client fallback
    let res = 0
    if (op === 'sqrt') {
      if (val < 0) {
        setDisplay('Invalid input')
        return
      }
      res = Math.sqrt(val)
    } else if (op === 'square') {
      res = Math.pow(val, 2)
    } else if (op === 'reciprocal') {
      if (val === 0) {
        setDisplay('Cannot divide by zero')
        return
      }
      res = 1 / val
    } else if (op === 'percent') {
      res = val / 100
    }
    const formatted = Number(res.toFixed(10)).toString()
    setDisplay(formatted)
    setIsNewCalculation(true)
  }

  const toggleHistory = async () => {
    const nextState = !showHistory
    setShowHistory(nextState)
    if (nextState && API_BASE) {
      try {
        const res = await fetch(`${API_BASE}/api/v1/calculator/history`)
        if (res.ok) {
          const data = await res.json()
          if (Array.isArray(data) && data.length > 0) {
            const apiItems = data.map(d => ({
              expr: d.expression,
              res: d.result,
              time: d.timestamp || ''
            }))
            setHistory(apiItems)
          }
        }
      } catch (err) {
        console.warn('History API fetch failed, keeping local ledger', err)
      }
    }
  }

  const handleClearHistory = async () => {
    setHistory([])
    if (API_BASE) {
      try {
        await fetch(`${API_BASE}/api/v1/calculator/history`, { method: 'DELETE' })
      } catch {
        // ignore offline
      }
    }
  }

  // Keyboard support
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key >= '0' && e.key <= '9') {
        handleDigit(e.key)
      } else if (e.key === '.') {
        if (!display.includes('.')) handleDigit('.')
      } else if (e.key === '+') {
        handleOperator('+')
      } else if (e.key === '-') {
        handleOperator('−')
      } else if (e.key === '*' || e.key === 'x') {
        handleOperator('×')
      } else if (e.key === '/') {
        e.preventDefault()
        handleOperator('÷')
      } else if (e.key === 'Enter' || e.key === '=') {
        e.preventDefault()
        handleEquals()
      } else if (e.key === 'Backspace') {
        handleBackspace()
      } else if (e.key === 'Escape') {
        handleClear()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [display, expression, isNewCalculation, evaluateMath])

  const copyToClipboard = () => {
    navigator.clipboard.writeText(display)
    showToastMsg('Copied to clipboard!')
  }

  return (
    <div className="calc-chassis">
      <div className="calc-bezel">
        {/* OLED Display Screen */}
        <div className="oled-screen" onClick={copyToClipboard} title="Click to copy result">
          <div className="oled-status">
            <span>● PRECISION STUDIO</span>
            <span>{API_BASE ? 'ONLINE API' : 'OFFLINE AST'}</span>
          </div>
          <div className="oled-expr">{expression}</div>
          <div className="oled-result">{display}</div>
        </div>

        {/* Mode Segmented Control */}
        <div className="mode-pills">
          <button 
            className={`pill-btn ${mode === 'standard' && !showHistory ? 'active' : ''}`}
            onClick={() => { setMode('standard'); setShowHistory(false); }}
          >
            Standard
          </button>
          <button 
            className={`pill-btn ${mode === 'scientific' && !showHistory ? 'active' : ''}`}
            onClick={() => { setMode('scientific'); setShowHistory(false); }}
          >
            Scientific
          </button>
          <button 
            className={`pill-btn ${showHistory ? 'active' : ''}`}
            onClick={toggleHistory}
          >
            🕒 History ({history.length})
          </button>
        </div>

        {/* History Drawer */}
        {showHistory ? (
          <div className="history-drawer">
            {history.length === 0 ? (
              <div className="history-empty">No calculations recorded yet.</div>
            ) : (
              history.map((item, idx) => (
                <div 
                  key={idx} 
                  className="history-item"
                  onClick={() => {
                    setDisplay(item.res)
                    setShowHistory(false)
                  }}
                >
                  <span>{item.expr} =</span>
                  <strong style={{ color: '#f59e0b' }}>{item.res}</strong>
                </div>
              ))
            )}
            {history.length > 0 && (
              <button 
                className="pill-btn" 
                style={{ width: '100%', marginTop: '10px', background: '#272732' }}
                onClick={handleClearHistory}
              >
                Clear History
              </button>
            )}
          </div>
        ) : (
          /* Keypad */
          <div className={`keypad-grid ${mode === 'scientific' ? 'grid-scientific' : 'grid-standard'}`}>
            {/* Scientific Row if active */}
            {mode === 'scientific' && (
              <>
                <button className="key-btn key-sci" onClick={() => handleScientific('sqrt')}>√x</button>
                <button className="key-btn key-sci" onClick={() => handleScientific('square')}>x²</button>
                <button className="key-btn key-sci" onClick={() => handleScientific('reciprocal')}>1/x</button>
                <button className="key-btn key-sci" onClick={() => handleScientific('percent')}>%</button>
                <button className="key-btn key-clear" onClick={handleClear}>AC</button>
              </>
            )}

            {mode === 'standard' && (
              <>
                <button className="key-btn key-clear" onClick={handleClear}>C</button>
                <button className="key-btn key-sci" onClick={handleBackspace}>⌫</button>
                <button className="key-btn key-sci" onClick={() => handleScientific('percent')}>%</button>
                <button className="key-btn key-op" onClick={() => handleOperator('÷')}>÷</button>
              </>
            )}

            {/* Standard Keypad Rows */}
            <button className="key-btn" onClick={() => handleDigit('7')}>7</button>
            <button className="key-btn" onClick={() => handleDigit('8')}>8</button>
            <button className="key-btn" onClick={() => handleDigit('9')}>9</button>
            <button className="key-btn key-op" onClick={() => handleOperator('×')}>×</button>
            {mode === 'scientific' && <button className="key-btn key-sci" onClick={handleBackspace}>⌫</button>}

            <button className="key-btn" onClick={() => handleDigit('4')}>4</button>
            <button className="key-btn" onClick={() => handleDigit('5')}>5</button>
            <button className="key-btn" onClick={() => handleDigit('6')}>6</button>
            <button className="key-btn key-op" onClick={() => handleOperator('−')}>−</button>
            {mode === 'scientific' && <button className="key-btn key-sci" onClick={() => handleDigit('(')}>(</button>}

            <button className="key-btn" onClick={() => handleDigit('1')}>1</button>
            <button className="key-btn" onClick={() => handleDigit('2')}>2</button>
            <button className="key-btn" onClick={() => handleDigit('3')}>3</button>
            <button className="key-btn key-op" onClick={() => handleOperator('+')}>+</button>
            {mode === 'scientific' && <button className="key-btn key-sci" onClick={() => handleDigit(')')}>)</button>}

            <button className="key-btn" style={{ gridColumn: mode === 'scientific' ? 'span 2' : 'span 1' }} onClick={() => handleDigit('0')}>0</button>
            <button className="key-btn" onClick={() => { if (!display.includes('.')) handleDigit('.') }}>.</button>
            <button className="key-btn key-equals" style={{ gridColumn: mode === 'scientific' ? 'span 2' : 'span 2' }} onClick={handleEquals}>=</button>
          </div>
        )}
      </div>

      {toast && (
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#059669',
          color: '#ffffff',
          padding: '8px 16px',
          borderRadius: '20px',
          fontSize: '0.82rem',
          fontWeight: '600',
          boxShadow: '0 4px 12px rgba(0,0,0,0.5)'
        }}>
          {toast}
        </div>
      )}
    </div>
  )
}
