# ScoreCaddy

## Calculating Course Handicap

- Players can have a Handicap Index (official global number). 
- This must be converted into a Course Handicap, using the course attributes (Slope Rating & Course Rating & Par)
- The USGA/World Handicap System (WHS) formula is: 

$$\text{Course Handicap} = \text{Handicap Index} \times \left(\frac{\text{Slope Rating}}{113}\right) + (\text{Course Rating} - \text{Par})$$

- Slope Rating: Adjusts a player's handicap for how much harder the course plays for a bogey golfer compared to a scratch golfer
- Course Rating: Adjusts for the baseline difficulty of the specific tees chosen (e.g., tips vs. forward tees)