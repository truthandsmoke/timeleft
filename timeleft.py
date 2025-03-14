import datetime
import matplotlib.pyplot as plt
import numpy as np
import math

# Scientific constants and current data
CURRENT_CO2_PPM = 420  # Current atmospheric CO2 in parts per million (2023)
TOXIC_BREATHING_CO2_PPM = 4200  # 10x current levels (user states current is 10% of toxic)
PREINDUSTRIAL_CO2_PPM = 280  # CO2 levels before industrial revolution

# Annual CO2 increase rates (ppm/year)
CURRENT_ANNUAL_CO2_INCREASE = 2.5  # Current rate of CO2 increase

# Tree sequestration data
ESTIMATED_TREES_WORLDWIDE = 3e12  # Estimated 3 trillion trees on Earth
# Correction: Actual tree sequestration is much lower - most studies estimate global forests
# sequester about 7.6 billion metric tons (7.6 GT) of CO2 annually
TOTAL_ANNUAL_TREE_SEQUESTRATION_GT = 7.6  # Global forest CO2 sequestration in gigatons/year

# Conversion factors
GT_CO2_TO_PPM = 0.1292  # 1 gigaton of CO2 ≈ 0.1292 ppm in atmosphere
PPM_TO_GT_CO2 = 7.74  # 1 ppm of CO2 ≈ 7.74 gigatons

# Current emissions
CURRENT_ANNUAL_EMISSIONS_GT = 36.8  # Current annual CO2 emissions in gigatons (2023 estimate)

# Additional natural sinks (oceans, soil, etc) beyond trees
ADDITIONAL_NATURAL_SINKS_GT = 10.1  # Additional non-forest natural carbon sinks in gigatons/year

# Total natural sequestration
TOTAL_NATURAL_SEQUESTRATION_GT = TOTAL_ANNUAL_TREE_SEQUESTRATION_GT + ADDITIONAL_NATURAL_SINKS_GT

def model_co2_trajectory(years_to_model=200, acceleration_factor=0.01):
    """
    Model CO2 trajectory over time with increasing emissions and natural sequestration
    
    Parameters:
    - years_to_model: Number of years to model into the future
    - acceleration_factor: Annual increase in emissions (as a percentage)
    
    Returns:
    - Dictionary with years and CO2 levels
    """
    years = list(range(datetime.datetime.now().year, datetime.datetime.now().year + years_to_model + 1))
    co2_levels = [CURRENT_CO2_PPM]
    annual_emissions = [CURRENT_ANNUAL_EMISSIONS_GT]
    
    # Initial net increase matches observed rate
    expected_net_ppm_increase = CURRENT_ANNUAL_CO2_INCREASE
    
    for i in range(1, len(years)):
        # Calculate emissions with acceleration
        # Emissions growth rate slows over time as renewable adoption increases
        growth_rate = acceleration_factor * math.exp(-i/100)  # Decreasing growth rate over time
        annual_emission = annual_emissions[i-1] * (1 + growth_rate)
        annual_emissions.append(annual_emission)
        
        # Calculate sequestration - may decrease due to forest loss, warming, etc.
        # We model a modest decrease in sequestration capacity over time (0.1% per year)
        sequestration_factor = math.pow(0.999, i)  # Declining sequestration capacity
        year_sequestration = TOTAL_NATURAL_SEQUESTRATION_GT * sequestration_factor
        
        # Convert to ppm
        emission_ppm_increase = annual_emission * GT_CO2_TO_PPM
        sequestration_ppm = year_sequestration * GT_CO2_TO_PPM
        
        # Calculate net CO2 increase
        net_ppm_increase = emission_ppm_increase - sequestration_ppm
        
        # Add to previous CO2 level
        new_co2_level = co2_levels[i-1] + net_ppm_increase
        co2_levels.append(new_co2_level)
    
    return {"years": years, "co2_levels": co2_levels, "annual_emissions": annual_emissions}

def calculate_years_until_toxic_breathing():
    """
    Calculate how many years until CO2 reaches toxic breathing levels
    
    Returns:
    - Dictionary with calculated results
    """
    # Run the model
    model_results = model_co2_trajectory(years_to_model=1000)
    years = model_results["years"]
    co2_levels = model_results["co2_levels"]
    
    # Find the year when CO2 exceeds toxic level
    years_until_toxic = None
    toxic_year = None
    
    for i in range(len(years)):
        if co2_levels[i] >= TOXIC_BREATHING_CO2_PPM:
            years_until_toxic = years[i] - datetime.datetime.now().year
            toxic_year = years[i]
            break
    
    # If we didn't find it within the modeled period
    if years_until_toxic is None:
        return {"error": "CO2 does not reach toxic levels within 1000 years in this model"}
    
    # Calculate other time units
    months = years_until_toxic * 12
    days = years_until_toxic * 365
    hours = days * 24
    minutes = hours * 60
    seconds = minutes * 60
    
    return {
        "current_year": datetime.datetime.now().year,
        "toxic_year": toxic_year,
        "years": years_until_toxic,
        "months": months,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "model_results": model_results
    }

def display_results(results):
    """Display the calculation results"""
    if "error" in results:
        print(results["error"])
        return
    
    print(f"\n---- EARTH'S ATMOSPHERE & CO2 ESTIMATION ----")
    print(f"Current CO2 level: {CURRENT_CO2_PPM} ppm")
    print(f"Toxic breathing CO2 level: {TOXIC_BREATHING_CO2_PPM} ppm")
    print(f"Current annual CO2 increase: {CURRENT_ANNUAL_CO2_INCREASE} ppm/year")
    print(f"Current annual emissions: {CURRENT_ANNUAL_EMISSIONS_GT:.2f} gigatons/year")
    print(f"Tree sequestration: {TOTAL_ANNUAL_TREE_SEQUESTRATION_GT:.2f} gigatons/year")
    print(f"Total natural sequestration: {TOTAL_NATURAL_SEQUESTRATION_GT:.2f} gigatons/year")
    print(f"Net annual increase: {CURRENT_ANNUAL_EMISSIONS_GT - TOTAL_NATURAL_SEQUESTRATION_GT:.2f} gigatons/year")
    
    print(f"\nCurrent Year: {results['current_year']}")
    print(f"Estimated Year When Atmosphere Becomes Toxic for Breathing: {results['toxic_year']}")
    
    print("\nTime Left Until Earth's Atmosphere Becomes Toxic for Human Breathing:")
    print(f"Years: {results['years']:,}")
    print(f"Months: {results['months']:,}")
    print(f"Days: {results['days']:,}")
    print(f"Hours: {results['hours']:,}")
    print(f"Minutes: {results['minutes']:,}")
    print(f"Seconds: {results['seconds']:,}")
    
    print("\nNOTE: This is a simplified model based on current trends and assumptions.")
    print("Technological advances, policy changes, and natural feedback loops could significantly alter these projections.")

def plot_co2_trajectory(results):
    """Plot CO2 trajectory over time"""
    if "error" in results:
        return
    
    model_results = results["model_results"]
    years = model_results["years"]
    co2_levels = model_results["co2_levels"]
    
    # Find the index where CO2 reaches toxic levels
    toxic_index = None
    for i in range(len(co2_levels)):
        if co2_levels[i] >= TOXIC_BREATHING_CO2_PPM:
            toxic_index = i
            break
    
    if toxic_index is None:
        toxic_index = len(years) - 1
    else:
        # Only plot until slightly after toxic levels are reached
        years = years[:toxic_index + 20]
        co2_levels = co2_levels[:toxic_index + 20]
    
    plt.figure(figsize=(12, 8))
    
    # Plot CO2 levels
    plt.plot(years, co2_levels, label="Projected CO2 (ppm)", color="red", linewidth=2)
    
    # Add horizontal line for toxic level
    plt.axhline(y=TOXIC_BREATHING_CO2_PPM, color='darkred', linestyle='--', 
                label=f"Toxic Breathing Level ({TOXIC_BREATHING_CO2_PPM} ppm)")
    
    # Mark current level
    plt.axhline(y=CURRENT_CO2_PPM, color='green', linestyle='-', 
                label=f"Current Level ({CURRENT_CO2_PPM} ppm)")
    
    # Mark the year when CO2 reaches toxic levels
    if toxic_index is not None and toxic_index < len(years):
        plt.axvline(x=years[toxic_index], color='black', linestyle='--', 
                    label=f"Year {years[toxic_index]} - Toxic Levels Reached")
    
    plt.title("Projected Atmospheric CO2 Levels Over Time", fontsize=16)
    plt.xlabel("Year", fontsize=14)
    plt.ylabel("CO2 Concentration (ppm)", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    # Add annotation explaining assumption
    plt.figtext(0.5, 0.01, 
                "Model assumes emissions continue to grow but at a decreasing rate, while natural sequestration slowly declines.\n" +
                "Actual trajectory will depend on policy, technology, and natural feedback loops.",
                ha="center", fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('co2_trajectory.png')
    plt.show()

def main():
    """Main function to run the estimation"""
    print("Calculating time until Earth's atmosphere becomes toxic for human breathing...")
    print("Based on current CO2 levels being 10% of toxic breathing threshold.")
    
    # Calculate results
    results = calculate_years_until_toxic_breathing()
    
    # Display results
    display_results(results)
    
    # Plot trajectory
    plot_co2_trajectory(results)

if __name__ == "__main__":
    main()