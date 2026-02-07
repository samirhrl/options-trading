import numpy as np
from scipy.stats import norm

class BlackScholes:
    """
    Implementation of the Black-Scholes model for pricing European options
    and calculating their Greeks (sensitivities).

    All methods are static and use standard Black-Scholes formulas.

    Method parameters:
        S : float
            Current price of the underlying asset
        K : float
            Strike price of the option
        T : float
            Time to maturity in years
        r : float
            Annual risk-free interest rate (continuously compounded)
        sigma : float
            Annual volatility of the underlying asset
        opt : str
            Option type, either "Call" or "Put"
    """

    @staticmethod
    def d1(S, K, T, r, sigma):
        """
        Calculates the d1 parameter in the Black-Scholes model.

        Formula: d1 = (ln(S/K) + (r + 0.5*sigma^2)*T) / (sigma * sqrt(T))

        @Returns:
            float : d1 value
        """
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    @staticmethod
    def d2(S, K, T, r, sigma):
        """
        Calculates the d2 parameter in the Black-Scholes model.

        Formula: d2 = d1 - sigma * sqrt(T)

        @Returns:
            float : d2 value
        """
        return BlackScholes.d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

    @staticmethod
    def price(S, K, T, r, sigma, opt):
        """
        Calculates the price of a European Call or Put option.

        Formulas:
            Call : C = S*N(d1) - K*exp(-r*T)*N(d2)
            Put  : P  = K*exp(-r*T)*N(-d2) - S*N(-d1)

        @Returns:
            float : option price
        """
        D1 = BlackScholes.d1(S, K, T, r, sigma)
        D2 = BlackScholes.d2(S, K, T, r, sigma)
        if opt == "Call":
            return S * norm.cdf(D1) - K * np.exp(-r * T) * norm.cdf(D2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-D2) - S * norm.cdf(-D1)

    @staticmethod
    def delta(S, K, T, r, sigma, opt):
        """
        Calculates the Delta of a European option.

        Delta measures sensitivity of the option price to changes in the underlying asset price.

        Formulas:
            Call : Δ = N(d1)
            Put  : Δ = N(d1) - 1

        @Returns:
            float : option Delta
        """
        D1 = BlackScholes.d1(S, K, T, r, sigma)
        return norm.cdf(D1) if opt == "Call" else norm.cdf(D1) - 1

    @staticmethod
    def gamma(S, K, T, r, sigma):
        """
        Calculates the Gamma of a European option.

        Gamma measures sensitivity of Delta to changes in the underlying asset price.

        Formula:
            Γ = N'(d1) / (S * sigma * sqrt(T))

        @Returns:
            float : option Gamma
        """
        D1 = BlackScholes.d1(S, K, T, r, sigma)
        return norm.pdf(D1) / (S * sigma * np.sqrt(T))

    @staticmethod
    def vega(S, K, T, r, sigma):
        """
        Calculates the Vega of a European option.

        Vega measures sensitivity of the option price to changes in volatility.

        Formula:
            ν = S * N'(d1) * sqrt(T)

        @Returns:
            float : option Vega
        """
        D1 = BlackScholes.d1(S, K, T, r, sigma)
        return S * norm.pdf(D1) * np.sqrt(T)

    @staticmethod
    def theta(S, K, T, r, sigma, opt):
        """
        Calculates the Theta of a European option.

        Theta measures sensitivity of the option price to time decay.

        Formulas:
            Call : θ = -S*N'(d1)*sigma/(2*sqrt(T)) - r*K*exp(-r*T)*N(d2)
            Put  : θ = -S*N'(d1)*sigma/(2*sqrt(T)) + r*K*exp(-r*T)*N(-d2)

        @Returns:
            float : option Theta
        """
        D1 = BlackScholes.d1(S, K, T, r, sigma)
        D2 = BlackScholes.d2(S, K, T, r, sigma)
        if opt == "Call":
            return -S * norm.pdf(D1) * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(D2)
        else:
            return -S * norm.pdf(D1) * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-D2)

    @staticmethod
    def rho(S, K, T, r, sigma, opt):
        """
        Calculates the Rho of a European option.

        Rho measures sensitivity of the option price to changes in the interest rate.

        Formulas:
            Call : ρ = K*T*exp(-r*T)*N(d2)
            Put  : ρ = -K*T*exp(-r*T)*N(-d2)

        @Returns:
            float : option Rho
        """
        D2 = BlackScholes.d2(S, K, T, r, sigma)
        if opt == "Call":
            return K * T * np.exp(-r * T) * norm.cdf(D2)
        else:
            return -K * T * np.exp(-r * T) * norm.cdf(-D2)
