# NBA Salary Prediction Model

This project trains a model to predict salary ratios for NBA players based on their performance in the season prior.

It uses machine learning to estimate a player's “fair market value” and identify over- and under-valued contracts.

## Introduction
**Idea**: Can historical data be used to predict the salary that an upcoming free agent in the NBA will earn?  

**Stakeholders**:
- NBA Teams:  
    - Use predictions to guide salary negotiations  
    - Identify underpaid players to target in trades  
- Players and Agents:  
    - Gain insight into the free agency market  
    - Use favorable predictions as leverage in contract negotiations  
    - Make informed decisions regarding contract offers and career moves  
- Sponsors and Advertisers:   
    - Assess player value for endorsements and sponsorship deals  
    - Identify future high-value players, primed to bring influence to a brand  

## Data
**1. Spotrac Active NBA Contracts Database**  
Features:  Player, POS: Primary position, AGE (at signing), START: Year contract begins, END: Year contract ends, Yrs: Contract length, Value: Total contract value, AAV: Average annual value of contract

**NBA Stats Kaggle Dataset, via NBA.com**  
Features: Player, Year, Team, regular season and playoff stats: GP, MIN, PTS, FGM, FGA, FG_PCT, FG3M, FG3A, FG3_PCT, FTM, FTA, FT_PCT, OREB, DREB, REB, AST, STL, BLK, TOV, PF

## Preprocessing 
### Cleaning and Feature Engineering
- Replace null playoff statistics with 0 (player’s team did not make playoffs)  
- Changing data types (Ex: Age from Object to Int64)  
- Fill missing age values with league median  
- Filter out non-standard contracts (10-day and two-way deals)  
- Pivot table so that playoff and regular season stats from the same season are counted as separate features in the same row, rather than separate rows.  
- Inner join deals and stats tables on player and year/season  
- Year season ended is matched with the year the contract was signed as contracts are signed during the following offseason.  
- Normalize our target variable across years by using salary ratio instead of pure salary  
    - salary ratio: A player’s salary as a percentage of the allowed maximum salary cap for that season.

## Model Selection
### Models
- Simple Regression: Linear, Lasso (L1), Ridge (L2)  
- Tree Methods: Decision Tree Regression  
- Ensemble Methods: Random Forests Regressor, XGBoost Regressor  

### Evaluation Metrics
- R-squared  
- RMSE: root mean squared error  
- MAE: mean absolute error  
- CV-Score: Mean of r-squared scores for 7 folds  

### Hyperparameter Tuning
- Random Search CV
    - Testing 50 random hyperparameter combos over 7 folds = 350 fits

## Model Performance
**CV-score**: 0.7480369811505753  
**R2**: 0.788152  
**RMSE**: 0.036285  
**MAE**: 0.022696  

## Author
Caedin Manners  
Data Science B.A.  
UC Berkely c/o 2025