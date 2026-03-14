import json
import sys

# Parameters: Lifespan model (wide_search Trial 22 - score 37/100)
# lap_time = base + M[tire] + max(0, age - LIFE[tire]) * D[tire] * (1 + T[tire] * (temp-25))

M_s = -0.992574425287819    # SOFT modifier (faster)
M_m = 0.0                    # MEDIUM modifier (reference)
M_h = 0.7941883348655359     # HARD modifier (slower initially)

D_s = 1.5153609944758606     # SOFT degradation per lap after life
D_m = 0.7696972875925806     # MEDIUM degradation per lap after life
D_h = 0.37602168520367785    # HARD degradation per lap after life

L_s = 10.039546754409935     # SOFT optimal performance laps (life)
L_m = 20.032737674541774     # MEDIUM optimal performance laps (life)
L_h = 29.921991928333313     # HARD optimal performance laps (life)

T_s = 0.030266323943183234   # SOFT temperature factor
T_m = 0.030203412631796156   # MEDIUM temperature factor
T_h = 0.03262899360130318    # HARD temperature factor

MODS  = {'SOFT': M_s, 'MEDIUM': M_m, 'HARD': M_h}
DEGS  = {'SOFT': D_s, 'MEDIUM': D_m, 'HARD': D_h}
LIFES = {'SOFT': L_s, 'MEDIUM': L_m, 'HARD': L_h}
TEMPS = {'SOFT': T_s, 'MEDIUM': T_m, 'HARD': T_h}


def simulate_race(race_config, strategies):
    base_lap_time = race_config['base_lap_time']
    pit_time = race_config['pit_lane_time']
    total_laps = race_config['total_laps']
    track_temp = race_config.get('track_temp', 25)
    temp_delta = track_temp - 25.0

    driver_times = {}

    for pos_key, strategy in strategies.items():
        driver_id = strategy['driver_id']
        current_tire = strategy['starting_tire']
        pit_stops = {stop['lap']: stop['to_tire'] for stop in strategy.get('pit_stops', [])}

        total_time = 0.0
        tire_age = 0

        for lap in range(1, total_laps + 1):
            tire_age += 1
            
            actual_deg = DEGS[current_tire] * (1.0 + TEMPS[current_tire] * temp_delta)
            degr_penalty = max(0.0, tire_age - LIFES[current_tire]) * actual_deg
            
            lap_time = base_lap_time + MODS[current_tire] + degr_penalty
            total_time += lap_time

            if lap in pit_stops:
                total_time += pit_time
                current_tire = pit_stops[lap]
                tire_age = 0

        driver_times[driver_id] = total_time

    sorted_drivers = sorted(driver_times.items(), key=lambda x: (x[1], x[0]))
    return [d[0] for d in sorted_drivers]


def main():
    input_data = sys.stdin.read()
    if not input_data.strip():
        return
    try:
        test_case = json.loads(input_data)
        predicted_positions = simulate_race(test_case['race_config'], test_case['strategies'])
        result = {"race_id": test_case["race_id"], "finishing_positions": predicted_positions}
        print(json.dumps(result, indent=2))
    except Exception:
        pass


if __name__ == "__main__":
    main()