# -*- coding: utf-8 -*-
from ABTypes import Variation
from typing import Tuple

TestResult = Tuple[float, float]  # type hint for tests output


def z_binomial_superiority_test(v1: Variation, v2: Variation, delta: float = 0.) -> TestResult:
    """
    Perform Test for Non-Inferiority/Superiority for Binomial samples.
    Returns test statistic and p-value.
    
    Method provided by Chow, Sample Size Calculations in Clinical Research (2nd ed., 2008), 4.2.2.
    
    p1 is the true mean of the first variation, p2 is the true mean of the second variation. 
    epsilon = p1 - p2.
    Null hypothesis H0: epsilon <= delta.
    Alternative hypothesis H1: epsilon > delta.
    
    :param v1: first variation
    :param v2: second variation
    :param delta: superiority margin
    :return: test statistic and p-value
    """
    from scipy.stats import norm
    from numpy import sqrt

    p1_hat = v1.estimate_conversion()
    p2_hat = v2.estimate_conversion()
    n1 = v1.total
    n2 = v2.total
    pe = p1_hat - p2_hat - delta  # point estimation
    var = p1_hat * (1 - p1_hat) / n1 + p2_hat * (1 - p2_hat) / n2  # variance estimation
    z = pe / sqrt(var)  # test statistic
    p_value = norm.sf(z)  # p-value

    return z, p_value


def z_binomial_test(v1: Variation, v2: Variation) -> TestResult:
    """
    Perform Test for comparison of binomial samples' means.
    Returns test statistic and p-value.
    
    Method provided by Kobzar AI, Applied Mathematical Statistics for Engineers and Scientists (2006), 4.1.3.1
    (Кобзарь А. И. Прикладная математческая статистика для инженеров и научных работников (2006), 4.1.3.1)
    
    p1 is the true mean of the first variation, p2 is the true mean of the second variation.
    Null hypothesis H0: p1 = p2.
    Alternative hypothesis H1: p1 > p2.
    
    :param v1: first variation
    :param v2: second variation
    :return: test statistic and p-value
    """
    from scipy.stats import norm
    from numpy import sqrt

    m1 = v1.success
    m2 = v2.success
    n1 = v1.total
    n2 = v2.total
    pe = m1 / n1 - m2 / n2 + 0.5 * (1 / n1 - 1 / n2)  # point estimation
    var = ((m1 + m2) / (n1 + n2) *
           (n1 + n2 - m1 - m2) / (n1 + n2) *
           (1 / n1 + 1 / n2)
           )  # variance estimation
    z = pe / sqrt(var)  # test statistic
    p_value = norm.sf(z)  # p-value

    return z, p_value


def f_binomial_test(v1: Variation, v2: Variation) -> TestResult:
    """
    Perform Fisher's Exact test of binomial samples' means.
    Returns test statistic and p-value.
    
    Method provided by G. Casella, L. Berger, Statistical Inference (2-nd ed., 2002), Example 8.3.30
    
    p1 is the true mean of the first variation, p2 is the true mean of the second variation.
    Null hypothesis H0: p1 = p2.
    Alternative hypothesis H1: p1 > p2.
    
    :param v1: first variation
    :param v2: second variation
    :return: test statistic and p-value
    """
    from numpy import array
    from scipy.stats import fisher_exact

    table = array([[v1.success, v2.success],
                   [v1.total - v1.success, v2.total - v2.success]
                   ])  # 2x2 contingency table
    return fisher_exact(table, 'greater')


def posterior_beta_parameters(variation: Variation, prior: Tuple[float, float] = (1, 1)) -> Tuple[float, float]:
    """
    Calculate parameters of posterior beta distribution under variation and prior beta parameters given.
    By default uninformative Beta(1, 1) prior is used.
    Proof may be found in [Wikipedia](https://en.wikipedia.org/wiki/Conjugate_prior).
    
    :param variation: variation (evidence)
    :param prior: parameters of prior Beta distribution
    :return: parameters of posterior beta distribution
    """
    a, b = prior
    c = variation.success
    n = variation.total
    return a + c, b + n - c


def prob_gt_beta(par1: Tuple[float, float], par2: Tuple[float, float], delta: float = 0) -> float:
    """
    Compute the probability Pr(p2 > p1 + delta) where p1 and p2 are independent random variables following Beta 
    distribution with parameters beta1 and par2 respectively.
    
    If delta > 0 uses exact integration approach provided by Chris Stucchio, Bayesian A/B Testing at VWO.
    If delta = 0 and conditions from Chris Stucchio, Asymptotics of Evan Miller's Bayesian A/B formula are hold uses 
    an approximation.
    Otherwise uses the sum approach provided by Evan Miller, Formulas for Bayesian A/B Testing
    
    :param par1: parameters of the 1st distribution
    :param par2: parameters of the 2nd distribution
    :param delta: margin. Should be greater or equal to 0.
    :return: probability of p2 > p1 + delta
    """
    from scipy.special import betaln
    from scipy.stats import beta
    from scipy.integrate import dblquad
    from numpy import log, exp

    if delta > 0:
        # Chris Stucchio, Bayesian A/B Testing at VWO
        def joint_density(y: float, x: float) -> float:
            """Joint density of two independent Beta r.vs."""
            return beta(*par1).pdf(x) * beta(*par2).pdf(y)
        prob = dblquad(joint_density, 0, 1, lambda a: a + delta, lambda a: 1)
        return prob[0]
    elif delta == 0:
        n = max(sum(par1), sum(par2)) - 2  # type: float
        psi = (par1[0] - 1) / n  # type: float
        phi = (par2[0] - 1) / n  # type: float

        if False and (n > 10**4) and (psi < phi <= 0.01):
            # Chris Stucchio, Asymptotics of Evan Miller's Bayesian A/B formula
            # TODO: This block should be revisited as its results are inadequate
            prob = log(2 / n / (phi - psi))
            prob += betaln(2 + n * (phi + psi), 2 + n * (2 - phi - psi))
            prob -= betaln(n * phi + 1, n * (1 - phi) + 1)
            prob -= betaln(n * psi + 1, n * (1 - psi) + 1)
            prob = exp(prob)
            return prob
        else:
            # Evan Miller, Formulas for Bayesian A/B Testing
            prob = 0
            a1, b1 = par1
            a2, b2 = par2
            for i in range(int(a2)):
                term = betaln(a1 + i, b1 + b2) - betaln(1 + i, b2) - betaln(a1, b1) - log(b2 + i)
                prob += exp(term)
            return prob
    else:
        raise Exception('delta >= 0 only.')


if __name__ == '__main__':
    import ABTypes

    var1 = list(map(int, input('Введите total и success первой вариации: ').split()))
    var1 = ABTypes.Variation(*var1)

    var2 = list(map(int, input('Введите total и success второй вариации: ').split()))
    var2 = ABTypes.Variation(*var2)

    tests = [z_binomial_superiority_test, z_binomial_test, f_binomial_test]
    for test in tests:
        print(test)
        print(test(var1, var2))
        print(test(var2, var1))
        print('-' * 80)

    beta1 = posterior_beta_parameters(var1)
    beta2 = posterior_beta_parameters(var2)

    print('Posterior beta for the 1st variation: ', beta1)
    print('Posterior beta for the 2nd variation: ', beta2)
    print('Probability p2 > p1: ', prob_gt_beta(beta1, beta2))
