"""
REI Nationwide LLC - Visualization Components
Clean, professional charts for the control tower dashboard
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List
import pandas as pd


# Color palette - professional, dark theme inspired
COLORS = {
    'primary': '#3B82F6',      # Blue
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Amber
    'danger': '#EF4444',       # Red
    'purple': '#8B5CF6',       # Purple
    'cyan': '#06B6D4',         # Cyan
    'gray': '#6B7280',         # Gray
    'dark': '#1F2937',         # Dark gray
    'light': '#F3F4F6',        # Light gray
}

CHUTE_COLORS = {
    'Internal': COLORS['primary'],
    'Wholesale': COLORS['success'],
    'Retail': COLORS['purple'],
    'Fallout': COLORS['gray'],
}


def create_kpi_metric(value: float, label: str, prefix: str = '$', 
                      suffix: str = '', delta: float = None, format_type: str = 'currency') -> Dict:
    """Format a KPI metric for display"""
    if format_type == 'currency':
        if value >= 1_000_000:
            display = f"{prefix}{value/1_000_000:.1f}M{suffix}"
        elif value >= 1_000:
            display = f"{prefix}{value/1_000:.0f}K{suffix}"
        else:
            display = f"{prefix}{value:.0f}{suffix}"
    elif format_type == 'number':
        display = f"{prefix}{value:.1f}{suffix}"
    elif format_type == 'percent':
        display = f"{prefix}{value*100:.1f}%{suffix}"
    else:
        display = f"{prefix}{value}{suffix}"
    
    return {'value': display, 'label': label, 'delta': delta}


def create_funnel_chart(leads: float, contracts: float, internal: float, 
                         wholesale: float, retail: float, fallout: float) -> go.Figure:
    """Create a horizontal funnel showing lead to outcome flow"""
    
    # Weekly annualized for perspective
    stages = ['Leads/Week', 'Contracts/Week', 'Internal', 'Wholesale', 'Retail', 'Fallout']
    values = [leads, contracts, internal, wholesale, retail, fallout]
    colors = [COLORS['cyan'], COLORS['primary'], COLORS['success'], 
              COLORS['purple'], COLORS['warning'], COLORS['gray']]
    
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textposition="inside",
        textinfo="value+percent initial",
        opacity=0.85,
        marker=dict(color=colors),
        connector=dict(line=dict(color="rgba(0,0,0,0)", width=0))
    ))
    
    fig.update_layout(
        title=dict(text="Weekly Pipeline Funnel", font=dict(size=16)),
        font=dict(size=12),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_revenue_breakdown_chart(wholesale: float, internal: float, 
                                    membership: float, listing: float, 
                                    prop_mgmt: float) -> go.Figure:
    """Donut chart for revenue breakdown"""
    
    labels = ['Wholesale Fees', 'Internal Acquisitions', 'Memberships', 
              'Listing Commissions', 'Property Mgmt']
    values = [wholesale, internal, membership, listing, prop_mgmt]
    colors = [COLORS['success'], COLORS['primary'], COLORS['purple'], 
              COLORS['warning'], COLORS['cyan']]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside',
        pull=[0.02, 0.02, 0, 0, 0]
    )])
    
    fig.update_layout(
        title=dict(text="Revenue Mix", font=dict(size=16)),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        annotations=[dict(
            text=f'${sum(values)/1e6:.1f}M',
            x=0.5, y=0.5,
            font_size=18,
            showarrow=False
        )]
    )
    
    return fig


def create_expense_breakdown_chart(president: float, acq: float, dispo: float,
                                    membership: float, marketing: float,
                                    exec_sal: float, staff_sal: float) -> go.Figure:
    """Horizontal bar chart for expenses"""
    
    categories = ['President Override', 'Acquisition Comm.', 'Dispo Comm.', 
                  'Membership Comm.', 'Marketing', 'Exec Salaries', 'Staff Salaries']
    values = [president, acq, dispo, membership, marketing, exec_sal, staff_sal]
    
    # Sort by value descending
    sorted_data = sorted(zip(categories, values), key=lambda x: x[1], reverse=True)
    categories = [x[0] for x in sorted_data]
    values = [x[1] for x in sorted_data]
    
    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker_color=COLORS['primary'],
        text=[f'${v/1000:.0f}K' for v in values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text="Expense Breakdown", font=dict(size=16)),
        height=350,
        margin=dict(l=20, r=80, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(showgrid=False)
    )
    
    return fig


def create_weekly_targets_chart(internal: float, wholesale: float, 
                                 retail: float, fallout: float,
                                 membership: float) -> go.Figure:
    """Bar chart showing weekly targets by category"""
    
    categories = ['Internal', 'Wholesale', 'Retail', 'Fallout', 'Memberships']
    values = [internal, wholesale, retail, fallout, membership]
    colors = [COLORS['primary'], COLORS['success'], COLORS['purple'], 
              COLORS['gray'], COLORS['warning']]
    
    fig = go.Figure(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f'{v:.1f}' for v in values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text="Weekly Outcome Targets", font=dict(size=16)),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        xaxis=dict(showgrid=False)
    )
    
    return fig


def create_staffing_chart(closers: float, underwriters: float, pms: float,
                          tcs: float, dispo: float, dscr: float) -> go.Figure:
    """Horizontal bar chart for staffing requirements"""
    
    roles = ['Closers', 'Underwriters', 'Project Mgrs', 'TCs', 'Dispo', 'DSCR Coord']
    needed = [closers, underwriters, pms, tcs, dispo, dscr]
    
    # Round up for actual headcount
    headcount = [max(1, int(n + 0.99)) for n in needed]
    
    fig = go.Figure()
    
    # Calculated need (fractional)
    fig.add_trace(go.Bar(
        y=roles,
        x=needed,
        name='Calculated Need',
        orientation='h',
        marker_color=COLORS['primary'],
        opacity=0.7,
        text=[f'{n:.1f}' for n in needed],
        textposition='inside'
    ))
    
    # Recommended headcount (rounded)
    fig.add_trace(go.Bar(
        y=roles,
        x=headcount,
        name='Recommended HC',
        orientation='h',
        marker_color=COLORS['success'],
        opacity=0.4,
        text=[f'{h}' for h in headcount],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text="Staffing Requirements", font=dict(size=16)),
        height=350,
        margin=dict(l=20, r=60, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        barmode='overlay',
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
        xaxis=dict(showgrid=True, gridcolor='rgba(128,128,128,0.2)'),
        yaxis=dict(showgrid=False)
    )
    
    return fig


def create_pipeline_split_chart(internal: float, wholesale: float, 
                                 retail: float, fallout: float) -> go.Figure:
    """Pie chart showing pipeline split percentages"""
    
    labels = ['Internal Retain', 'Wholesale', 'Retail Listing', 'Fallout/Nurture']
    values = [internal, wholesale, retail, fallout]
    colors = [COLORS['primary'], COLORS['success'], COLORS['purple'], COLORS['gray']]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='inside'
    )])
    
    fig.update_layout(
        title=dict(text="Pipeline Split", font=dict(size=16)),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    
    return fig


def create_scenario_comparison_chart(scenarios: List[Dict]) -> go.Figure:
    """Bar chart comparing key metrics across scenarios"""
    
    if len(scenarios) < 2:
        return None
    
    metrics = ['Gross Revenue', 'NOI', 'Contracts/Week', 'Leads/Week']
    
    fig = make_subplots(rows=2, cols=2, subplot_titles=metrics)
    
    colors = [COLORS['primary'], COLORS['success'], COLORS['purple'], COLORS['warning']]
    
    for idx, scenario in enumerate(scenarios[:4]):  # Max 4 scenarios
        name = scenario.get('name', f'Scenario {idx+1}')
        color = colors[idx % len(colors)]
        
        # Gross Revenue
        fig.add_trace(go.Bar(
            x=[name], 
            y=[scenario.get('gross_revenue', 0)],
            name=name,
            marker_color=color,
            showlegend=True if idx == 0 else False,
            legendgroup=name
        ), row=1, col=1)
        
        # NOI
        fig.add_trace(go.Bar(
            x=[name], 
            y=[scenario.get('noi', 0)],
            name=name,
            marker_color=color,
            showlegend=False,
            legendgroup=name
        ), row=1, col=2)
        
        # Contracts/Week
        fig.add_trace(go.Bar(
            x=[name], 
            y=[scenario.get('contracts_per_week', 0)],
            name=name,
            marker_color=color,
            showlegend=False,
            legendgroup=name
        ), row=2, col=1)
        
        # Leads/Week
        fig.add_trace(go.Bar(
            x=[name], 
            y=[scenario.get('leads_per_week', 0)],
            name=name,
            marker_color=color,
            showlegend=False,
            legendgroup=name
        ), row=2, col=2)
    
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.08)
    )
    
    return fig


def create_sensitivity_heatmap(data: List[Dict], title: str, 
                                value_col: str, row_col: str) -> go.Figure:
    """Create a styled table/heatmap for sensitivity analysis"""
    
    df = pd.DataFrame(data)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color=COLORS['dark'],
            font=dict(color='white', size=12),
            align='center',
            height=30
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color=[COLORS['light']],
            font=dict(color=COLORS['dark'], size=11),
            align='center',
            height=25
        )
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_proforma_waterfall(revenue: float, expenses_breakdown: Dict, noi: float) -> go.Figure:
    """Waterfall chart from gross revenue to NOI"""
    
    labels = ['Gross Revenue']
    values = [revenue]
    measures = ['absolute']
    
    for name, amount in expenses_breakdown.items():
        labels.append(name)
        values.append(-amount)
        measures.append('relative')
    
    labels.append('NOI')
    values.append(noi)
    measures.append('total')
    
    fig = go.Figure(go.Waterfall(
        orientation='v',
        measure=measures,
        x=labels,
        y=values,
        connector=dict(line=dict(color='rgb(63, 63, 63)')),
        decreasing=dict(marker=dict(color=COLORS['danger'])),
        increasing=dict(marker=dict(color=COLORS['success'])),
        totals=dict(marker=dict(color=COLORS['primary']))
    ))
    
    fig.update_layout(
        title=dict(text="Revenue to NOI Waterfall", font=dict(size=16)),
        height=400,
        margin=dict(l=20, r=20, t=50, b=100),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickangle=45)
    )
    
    return fig


def alert_color(severity: str) -> str:
    """Get color for alert severity"""
    return COLORS['danger'] if severity == 'critical' else COLORS['warning']


def format_currency(value: float) -> str:
    """Format number as currency string"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif value >= 1_000:
        return f"${value/1_000:.1f}K"
    else:
        return f"${value:.0f}"


def format_number(value: float, decimals: int = 1) -> str:
    """Format number with specified decimals"""
    return f"{value:.{decimals}f}"


def format_percent(value: float) -> str:
    """Format decimal as percentage"""
    return f"{value*100:.1f}%"
