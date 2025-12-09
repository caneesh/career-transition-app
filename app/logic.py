from app.models import FinancialProfile, TransitionPlan


class FinancialBridge:
    """
    Financial calculator for career transitions.
    Analyzes burn rate, runway, and capital gaps.
    """

    def __init__(self, profile: FinancialProfile):
        self.profile = profile

    def calculate_burn_rate(self) -> float:
        """
        Calculate monthly burn rate (monthly expenses).
        Returns: Monthly spending amount
        """
        return self.profile.monthly_expenses

    def calculate_runway(self) -> float:
        """
        Calculate financial runway in months.
        Returns: Number of months current savings will last
        """
        burn_rate = self.calculate_burn_rate()
        if burn_rate == 0:
            return float('inf')
        return self.profile.current_savings / burn_rate

    def calculate_capital_gap(self) -> float:
        """
        Calculate capital gap for the transition period.
        Negative value means surplus, positive means additional capital needed.
        Returns: Capital gap amount
        """
        required_capital = self.profile.monthly_expenses * self.profile.transition_months
        return required_capital - self.profile.current_savings

    def calculate_emergency_fund(self) -> float:
        """
        Calculate recommended emergency fund amount.
        Returns: Emergency fund amount (months of expenses)
        """
        return self.profile.monthly_expenses * self.profile.emergency_fund_months

    def calculate_total_capital_needed(self) -> float:
        """
        Calculate total capital needed for safe transition.
        Includes transition period + emergency fund.
        Returns: Total capital required
        """
        transition_capital = self.profile.monthly_expenses * self.profile.transition_months
        emergency_fund = self.calculate_emergency_fund()
        return transition_capital + emergency_fund

    def is_financially_ready(self) -> bool:
        """
        Determine if financially ready for transition.
        Returns: True if current savings cover transition + emergency fund
        """
        total_needed = self.calculate_total_capital_needed()
        return self.profile.current_savings >= total_needed

    def generate_recommendations(self) -> list[str]:
        """
        Generate personalized financial recommendations.
        Returns: List of actionable recommendations
        """
        recommendations = []
        runway = self.calculate_runway()
        capital_gap = self.calculate_capital_gap()
        total_needed = self.calculate_total_capital_needed()

        # Runway assessment
        if runway < self.profile.transition_months:
            recommendations.append(
                f"WARNING: Your current runway ({runway:.1f} months) is less than your transition period "
                f"({self.profile.transition_months} months). Consider building more savings."
            )
        elif runway < self.profile.transition_months + self.profile.emergency_fund_months:
            recommendations.append(
                f"WARNING: You have {runway:.1f} months of runway, but need additional buffer for emergency fund."
            )
        else:
            recommendations.append(
                f"GOOD: You have {runway:.1f} months of runway, which covers your transition period."
            )

        # Capital gap assessment
        if capital_gap > 0:
            recommendations.append(
                f"CAPITAL NEEDED: You need an additional ${capital_gap:,.2f} to cover your {self.profile.transition_months}-month transition."
            )
        else:
            recommendations.append(
                f"GOOD: You have sufficient savings (${abs(capital_gap):,.2f} surplus) for the transition period."
            )

        # Emergency fund assessment
        emergency_fund = self.calculate_emergency_fund()
        if self.profile.current_savings < total_needed:
            shortfall = total_needed - self.profile.current_savings
            recommendations.append(
                f"ANALYSIS: Total capital needed (transition + emergency fund): ${total_needed:,.2f}. "
                f"You're ${shortfall:,.2f} short."
            )
        else:
            recommendations.append(
                f"GOOD: You have adequate savings for both transition and {self.profile.emergency_fund_months}-month emergency fund."
            )

        # Expense reduction suggestion
        if capital_gap > 0:
            potential_savings = self.profile.monthly_expenses * 0.2  # 20% reduction
            new_gap = (self.profile.monthly_expenses - potential_savings) * self.profile.transition_months - self.profile.current_savings
            if new_gap < capital_gap:
                recommendations.append(
                    f"TIP: Reducing expenses by 20% (${potential_savings:,.2f}/month) could decrease your capital gap to ${max(0, new_gap):,.2f}."
                )

        # Salary comparison (if new salary provided)
        if self.profile.new_salary:
            income_change = ((self.profile.new_salary - self.profile.current_salary) / self.profile.current_salary) * 100
            if income_change < -20:
                recommendations.append(
                    f"WARNING: Your new salary represents a {abs(income_change):.1f}% decrease. Ensure your budget accounts for this."
                )
            elif income_change > 20:
                recommendations.append(
                    f"GOOD: Your new salary represents a {income_change:.1f}% increase - great financial move!"
                )

        return recommendations

    def analyze(self) -> TransitionPlan:
        """
        Perform complete financial analysis.
        Returns: TransitionPlan with all calculations and recommendations
        """
        return TransitionPlan(
            monthly_burn_rate=self.calculate_burn_rate(),
            total_runway_months=self.calculate_runway(),
            capital_gap=self.calculate_capital_gap(),
            emergency_fund_needed=self.calculate_emergency_fund(),
            total_capital_needed=self.calculate_total_capital_needed(),
            is_financially_ready=self.is_financially_ready(),
            recommendations=self.generate_recommendations()
        )
