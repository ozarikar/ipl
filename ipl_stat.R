library(openintro)
library(ggplot2)
library(car)
library(mosaic)


null <- glm( Team1_Won~1,games_summary, family = 'binomial')
full <- glm(Team1_Won~ ., games_summary, family = 'binomial')
summary(null)
step(null, scope =list(upper = full),direction = 'forward')
step(full, scope =list(lower = null),direction = 'backward')
step(null, scope =list(upper = full, upper = full))


#checking multi coliner
with(games_summary,cor(data.frame(Team1_Won,BowlersUsed_Margin_Overall,DotBalls_Margin_Overall,ExtrasConceded_Margin_Overall,Runs_Margin_Powerplay,Runs_Margin_MiddleOvers, Runs_Margin_DeathOvers,          Fours_Margin_Powerplay,          Fours_Margin_MiddleOvers ,Fours_Margin_DeathOvers,         Sixes_Margin_Powerplay,Sixes_Margin_MiddleOvers,       
                                  Sixes_Margin_DeathOvers,         WicketsTaken_Margin_Powerplay,   WicketsTaken_Margin_MiddleOvers,
                                  WicketsTaken_Margin_DeathOvers)))


win_lm <- glm(Team1_Won~ DotBalls_Margin_Overall+   
              Runs_Margin_MiddleOvers +Fours_Margin_MiddleOvers  +  Runs_Margin_Powerplay  +
                Fours_Margin_DeathOvers  +
              Sixes_Margin_DeathOvers  +  ExtrasConceded_Margin_Overall  +
              WicketsTaken_Margin_MiddleOvers,
              data = games_summary,family = 'binomial')




win_lm <- glm(Team1_Won~    
                DotBalls_Margin_Overall   +  Runs_Margin_Powerplay  +
                Fours_Margin_DeathOvers  +
                Sixes_Margin_DeathOvers  +  ExtrasConceded_Margin_Overall  +
                WicketsTaken_Margin_MiddleOvers,
              data = games_summary,family = 'binomial')


summary(win_lm)


# resid plots
crPlots(win_lm)
crPlot(win_lm,'Runs_Margin_MiddleOvers')






#####

null <- glm( Team1_Won~1,game_summary_overall, family = 'binomial')
full <- glm(Team1_Won~ ., game_summary_overall, family = 'binomial')
summary(null)
step(null, scope =list(upper = full),direction = 'forward')
step(full, scope =list(lower = null),direction = 'backward')
step(null, scope =list(upper = full, upper = full))


#checking multi coliner
with(games_summary,cor(data.frame(Team1_Won,BowlersUsed_Margin_Overall,DotBalls_Margin_Overall,ExtrasConceded_Margin_Overall,Runs_Margin_Powerplay,Runs_Margin_MiddleOvers, Runs_Margin_DeathOvers,          Fours_Margin_Powerplay,          Fours_Margin_MiddleOvers ,Fours_Margin_DeathOvers,         Sixes_Margin_Powerplay,Sixes_Margin_MiddleOvers,       
                                  Sixes_Margin_DeathOvers,         WicketsTaken_Margin_Powerplay,   WicketsTaken_Margin_MiddleOvers,
                                  WicketsTaken_Margin_DeathOvers)))

win_lm <- glm (  Team1_Won~   WicketsTaken_Margin_Overall +  ExtrasConceded_Margin_Overall+
                                  Sixes_Margin_Overall     +      Fours_Margin_Overall    +    
                                  Runs_Margin_Powerplay       +  Runs_Margin_DeathOvers,data= game_summary_overall,family= 'binomial'  )




win_lm <- glm(Team1_Won~  DotBalls_Margin_Overall + 
                            Runs_Margin_Powerplay  +
                Fours_Margin_Overall  +
                Sixes_Margin_Overall  +  ExtrasConceded_Margin_Overall,
              data = game_summary_overall,family = 'binomial')





win_lm <- glm(Team1_Won~  DotBalls_Margin_Overall +
                Runs_Margin_Powerplay*ExtrasConceded_Margin_Overall+ Fours_Margin_Overall+Sixes_Margin_Overall 
                    ,
              data = game_summary_overall,family = 'binomial')


summary(win_lm)


predic = predict(win_lm, data.frame(DotBalls_Margin_Overall = 2, Runs_Margin_Powerplay = -6,
                                    Fours_Margin_Overall =-3 ,Sixes_Margin_Overall=-5 ,
                                    ExtrasConceded_Margin_Overall= -8), se = TRUE)
predic

qt(.05, 141)
plogis(predic$fit-1.655732*predic$se.fit)
plogis(predic$fit+1.655732*predic$se.fit)



# resid plots
crPlots(win_lm)
crPlot(win_lm,'Runs_Margin_MiddleOvers')

