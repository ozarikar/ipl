# nolint start
library(dplyr)
library(tidyr)
library(magrittr) # Ensure the pipe operator is available

ipl_data_2023 <- read.csv("ipl_data_2023.csv")
ipl_data_2024 <- read.csv("ipl_data_2024.csv")
ipl_data_2025 <- read.csv("ipl_data_2025.csv")

# Combine the data frames
ipl_data <- bind_rows(ipl_data_2023, ipl_data_2024, ipl_data_2025)
write.csv(ipl_data, "ipl_data_combined.csv", row.names = FALSE)
# Remove rows with NA in specific columns

required_columns <- c("MatchID", "TeamName")
ipl_data <- ipl_data %>% filter(!if_any(all_of(required_columns), is.na))

game_names <- unique(ipl_data$MatchID,na.rm = TRUE)



View(ipl_data)
games_stat <- data.frame(
    MatchID = numeric(),
    ATeamName = character(),
    BTeamName = character(),
    ATeamScore = numeric(),
    BTeamScore = numeric(),
    ATeamFours = numeric(),
    BTeamFours = numeric(),
    ATeamSixes = numeric(),
    BTeamSixes = numeric(),
    PowerPlay = numeric(),
    total_runs = numeric(),
    A_fifties = numeric(),
    B_fifties = numeric()
)


for (game in game_names) {
    game_data <- ipl_data %>% 
        filter(MatchID == game)
    if(nrow(game_data) > 0) {
        # Extracting team names
        team_names <- unique(game_data$TeamName[game_data$TeamName != "" & !is.na(game_data$TeamName)]) # nolint
        
        if (length(team_names) != 2 || any(is.na(team_names))) {
            print(paste("Error: Expected 2 valid teams, found", length(team_names), "in game", game, "with teams:", paste(team_names, collapse = ", ")))
            next
        }
        ATeamName <- team_names[1]
        print(paste0("ATeamName:  ", ATeamName))
        BTeamName <- team_names[2]
        print(paste0("BTeamName:  ", BTeamName))


       # Extracting scores
        ATeamScore <- sum(as.numeric(gsub("\\s*\\(.*\\)", "", game_data$Runs[game_data$TeamName == ATeamName])),na.rm = TRUE)
        print(paste0("ATeamScore", ATeamScore))
        BTeamScore <- sum(as.numeric(gsub("\\s*\\(.*\\)", "", game_data$Runs[game_data$TeamName == BTeamName])),na.rm = TRUE)
        print(paste0("BTeamScore", BTeamScore))
        
        # Extracting fours and sixes
        ATeamFours <- sum(as.numeric(game_data$IsFour[game_data$TeamName == ATeamName]),na.rm = TRUE)
        BTeamFours <- sum(as.numeric(game_data$IsFour[game_data$TeamName == BTeamName]),na.rm = TRUE)
        ATeamSixes <- sum(as.numeric(game_data$IsSix[game_data$TeamName == ATeamName]),na.rm = TRUE)
        BTeamSixes <- sum(as.numeric(game_data$IsSix[game_data$TeamName == BTeamName]),na.rm = TRUE)
        
        # Extracting powerplay runs
        ATeamPowerPlay <- as.numeric(game_data$TotalRuns[game_data$TeamName == ATeamName & game_data$OverNo == 6 & game_data$BallNo == 6])
        BTeamPowerPlay <- as.numeric(game_data$TotalRuns[game_data$TeamName == BTeamName & game_data$OverNo == 6 & game_data$BallNo == 6])
        
        # Extracting total runs
        total_runs <- ATeamScore + BTeamScore
        
        # Extracting fifties
        A_fifties <- sum(as.numeric(game_data$Fifties[game_data$Player == ATeamName]),na.rm = TRUE)
        B_fifties <- sum(as.numeric(game_data$Fifties[game_data$Player == BTeamName]), na.rm = TRUE)
        # Adding to the data frame
        if (!is.na(ATeamName) && !is.na(BTeamName) && 
            length(ATeamName) > 0 && length(BTeamName) > 0 &&
            length(ATeamScore) > 0 && length(BTeamScore) > 0) {
            games_stat <- rbind(games_stat, data.frame(
                MatchID = as.numeric(game),
                ATeamName = ifelse(length(ATeamName) == 0, NA, ATeamName),
                BTeamName = ifelse(length(BTeamName) == 0, NA, BTeamName),
                ATeamScore = ifelse(length(ATeamScore) == 0 || is.na(ATeamScore), 0, ATeamScore),
                BTeamScore = ifelse(length(BTeamScore) == 0 || is.na(BTeamScore), 0, BTeamScore),
                ATeamFours = ifelse(length(ATeamFours) == 0 || is.na(ATeamFours), 0, ATeamFours),
                BTeamFours = ifelse(length(BTeamFours) == 0 || is.na(BTeamFours), 0, BTeamFours),
                ATeamSixes = ifelse(length(ATeamSixes) == 0 || is.na(ATeamSixes), 0, ATeamSixes),
                BTeamSixes = ifelse(length(BTeamSixes) == 0 || is.na(BTeamSixes), 0, BTeamSixes),
                PowerPlay = (ifelse(length(ATeamPowerPlay) == 0 || all(is.na(ATeamPowerPlay)), 0, sum(ATeamPowerPlay, na.rm = TRUE)))-
                 ifelse(length(BTeamPowerPlay) == 0 || all(is.na(BTeamPowerPlay)), 0, sum(BTeamPowerPlay, na.rm = TRUE)),
                total_runs = ifelse(length(total_runs) == 0 || is.na(total_runs), 0, total_runs),
                A_fifties = ifelse(length(A_fifties) == 0 || is.na(A_fifties), 0, A_fifties),
                B_fifties = ifelse(length(B_fifties) == 0 || is.na(B_fifties), 0, B_fifties)))
        } else {
            print(paste("Skipping game", game, "due to missing or invalid data"))
        }
    }
}

View(games_stat)
write.csv(games_stat, "games_stat_2023.csv", row.names = FALSE)
# nolint end