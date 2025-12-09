
summarize

regress bf_won isnight bf_fours bf_sixes bf_extras bs_fours bs_sixes bs_extras bf_pp_margin

vif

estat hettest
reg bf_won isnight bf_fours bf_sixes bf_extras bs_fours bs_sixes bs_extras bf_pp_margin, robust

logit bf_won isnight bf_fours bf_sixes bf_extras bs_fours bs_sixes bs_extras bf_pp_margin

margins, dydx(*) 

logit bf_won isnight bf_fours bf_sixes bf_extras bs_fours bs_sixes bs_extras bf_pp_margin, robust

estat classification

newey bf_won isnight bf_fours bf_sixes bf_extras bs_fours bs_sixes bs_extras bf_pp_margin, lag(4)
