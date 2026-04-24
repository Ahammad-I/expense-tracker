import { useEffect, useState } from 'react'
import { fetchExpenses, createExpense } from './api/expenses'

function App() {
  const [expenses, setExpenses] = useState([])
  const [total, setTotal] = useState('0')

  const [category, setCategory] = useState('')
  const [sort, setSort] = useState('date_desc')

  const [form, setForm] = useState({
    amount: '',
    category: 'food',
    description: '',
    date: ''
  })

  const inputStyle = {
    height: '45px',
    padding: '10px',
    margin: '10px 0',
    fontSize: '16px',
    width: '300px',
    borderRadius: '6px',
    border: '1px solid #ccc',
    display: 'block'
  }

  function validateForm({ amount, description, date }) {
    const errors = {}

    if (!amount) errors.amount = "Amount is required"
    if (!description?.trim()) errors.description = "Description is required"
    if (!date) errors.date = "Date is required"

    return errors
  }

  async function loadExpenses() {
    try {
      const data = await fetchExpenses({ category, sort })
      setExpenses(data.results)
      setTotal(data.total)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    loadExpenses()
  }, [category, sort])

  async function handleSubmit(e) {
    e.preventDefault()

    const errors = validateForm(form)

    if (Object.keys(errors).length > 0) {
      alert(Object.entries(errors).map(([k, v]) => `${k}: ${v}`).join('\n'))
      return
    }

    try {
      await createExpense(form)

      setForm({
        amount: '',
        category: 'food',
        description: '',
        date: ''
      })

      await loadExpenses()

    } catch (err) {
      if (err.details) {
        alert(
          Object.entries(err.details)
            .map(([f, msgs]) => `${f}: ${msgs.join(', ')}`)
            .join('\n')
        )
      } else {
        alert(err.message)
      }
    }
  }

  return (
    <div style={{ padding: '30px', color: 'white' }}>
      <h1>Expense Tracker</h1>

      {/* FILTERS */}
      <h3>Filters</h3>

      <select value={category} onChange={e => setCategory(e.target.value)} style={inputStyle}>
        <option value="">All</option>
        <option value="food">Food</option>
        <option value="transport">Transport</option>
        <option value="shopping">Shopping</option>
      </select>

      <select value={sort} onChange={e => setSort(e.target.value)} style={inputStyle}>
        <option value="date_desc">Newest First</option>
        <option value="date_asc">Oldest First</option>
      </select>

      <h3>Total: ₹{total}</h3>

      {/* FORM */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '30px' }}>
        <input
          placeholder="Amount"
          value={form.amount}
          onChange={e => setForm({ ...form, amount: e.target.value })}
          style={inputStyle}
        />

        <input
          placeholder="Description"
          value={form.description}
          onChange={e => setForm({ ...form, description: e.target.value })}
          style={inputStyle}
        />

        <input
          type="date"
          value={form.date}
          onChange={e => setForm({ ...form, date: e.target.value })}
          style={inputStyle}
        />

        <select
          value={form.category}
          onChange={e => setForm({ ...form, category: e.target.value })}
          style={inputStyle}
        >
          <option value="food">Food</option>
          <option value="transport">Transport</option>
          <option value="shopping">Shopping</option>
        </select>

        <button
          type="submit"
          style={{
            height: '45px',
            padding: '10px 20px',
            fontSize: '16px',
            marginTop: '10px',
            cursor: 'pointer',
            borderRadius: '6px',
            border: 'none',
            backgroundColor: '#4CAF50',
            color: 'white'
          }}
        >
          Add Expense
        </button>
      </form>

      {/* LIST */}
      <h2>Expenses</h2>
      {expenses.map(e => (
        <div key={e.id} style={{ marginBottom: '10px' }}>
          ₹{e.amount} - {e.category_display} - {e.description}
        </div>
      ))}
    </div>
  )
}

export default App