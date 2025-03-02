from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from simulation.engine import SimulationEngine

# Define the blueprint for simulation routes
simulation_bp = Blueprint('simulation', __name__)

# We'll use the sim_engine from app.py instead of creating a new one here
sim_engine = None  # This will be set by init_app

@simulation_bp.route('/new', methods=['GET'])
def new_simulation():
    """Show the new simulation form"""
    teams = list(sim_engine.teams.keys()) if sim_engine.teams else []
    return render_template('simulation/setup.html', teams=teams)

@simulation_bp.route('/run', methods=['POST'])
def run_simulation():
    """Run a simulation based on form data"""
    try:
        home_team_id = request.form.get('home_team')
        away_team_id = request.form.get('away_team')
        num_simulations = int(request.form.get('num_simulations', 1))
        
        # If multiple simulations requested, redirect to the multiple simulation route
        if num_simulations > 1:
            return redirect(url_for('simulation.run_multiple_simulations', 
                                   home_team=home_team_id, 
                                   away_team=away_team_id, 
                                   num_sims=num_simulations))
        
        # Validate inputs
        if not home_team_id or not away_team_id:
            flash("Please select both teams", "error")
            return redirect(url_for('simulation.new_simulation'))
            
        # Get team objects
        home_team = sim_engine.get_team(home_team_id)
        away_team = sim_engine.get_team(away_team_id)
        
        if not home_team or not away_team:
            flash("Invalid team selection", "error")
            return redirect(url_for('simulation.new_simulation'))
        
        # Run simulation
        results = sim_engine.simulate_game(home_team, away_team, verbose=True)
        
        # Add simulation_type to results
        results['simulation_type'] = 'single'
        results['home_team_name'] = home_team.name
        results['away_team_name'] = away_team.name
        results['home_score'] = results['home_team']['score']
        results['away_score'] = results['away_team']['score']
        results['winner'] = home_team.name if results['home_score'] > results['away_score'] else away_team.name if results['away_score'] > results['home_score'] else "Tie"
        results['plays'] = results['total_plays']
        
        # Process player stats for display
        home_players = []
        away_players = []
        
        # Format player stats for the template
        home_player_stats = []
        away_player_stats = []
        
        # Check for player stats
        if 'player_stats' in results:
            for player_id, stats in results['player_stats'].items():
                team_id = stats.get('team_id', '')
                
                # Create a player object with stats
                player_obj = {
                    'id': player_id,
                    'name': stats.get('player_name', 'Unknown'),
                    'position': stats.get('position', ''),
                    'team': team_id,
                    'has_stats': True,
                    'stats': {}
                }
                
                # Add position-specific stats
                if stats.get('position') == 'QB':
                    player_obj['stats'] = {
                        'passing_attempts': stats.get('pass_attempts', 0),
                        'passing_completions': stats.get('pass_completions', 0),
                        'passing_yards': stats.get('pass_yards', 0),
                        'passing_tds': stats.get('pass_tds', 0),
                        'passing_ints': stats.get('interceptions', 0),
                        'rushing_attempts': stats.get('rush_attempts', 0),
                        'rushing_yards': stats.get('rush_yards', 0),
                        'rushing_tds': stats.get('rush_tds', 0)
                    }
                elif stats.get('position') == 'RB':
                    player_obj['stats'] = {
                        'rushing_attempts': stats.get('rush_attempts', 0),
                        'rushing_yards': stats.get('rush_yards', 0),
                        'rushing_tds': stats.get('rush_tds', 0),
                        'receiving_targets': stats.get('targets', 0),
                        'receiving_catches': stats.get('receptions', 0),
                        'receiving_yards': stats.get('receiving_yards', 0),
                        'receiving_tds': stats.get('receiving_tds', 0)
                    }
                elif stats.get('position') in ['WR', 'TE']:
                    player_obj['stats'] = {
                        'receiving_targets': stats.get('targets', 0),
                        'receiving_catches': stats.get('receptions', 0),
                        'receiving_yards': stats.get('receiving_yards', 0),
                        'receiving_tds': stats.get('receiving_tds', 0)
                    }
                
                # Add to appropriate team list
                if team_id == home_team.id:
                    home_player_stats.append(player_obj)
                elif team_id == away_team.id:
                    away_player_stats.append(player_obj)
        
        # Add team stats
        home_stats = {
            'total_yards': sum(p['stats'].get('passing_yards', 0) + p['stats'].get('rushing_yards', 0) for p in home_player_stats),
            'passing_yards': sum(p['stats'].get('passing_yards', 0) for p in home_player_stats),
            'rushing_yards': sum(p['stats'].get('rushing_yards', 0) for p in home_player_stats),
            'turnovers': sum(p['stats'].get('passing_ints', 0) for p in home_player_stats)
        }
        
        away_stats = {
            'total_yards': sum(p['stats'].get('passing_yards', 0) + p['stats'].get('rushing_yards', 0) for p in away_player_stats),
            'passing_yards': sum(p['stats'].get('passing_yards', 0) for p in away_player_stats),
            'rushing_yards': sum(p['stats'].get('rushing_yards', 0) for p in away_player_stats),
            'turnovers': sum(p['stats'].get('passing_ints', 0) for p in away_player_stats)
        }
        
        # Add stats to results
        results['home_stats'] = home_stats
        results['away_stats'] = away_stats
        results['home_player_stats'] = home_player_stats
        results['away_player_stats'] = away_player_stats
        
        # Check for web-formatted player stats
        if 'player_stats_web' in results:
            for player in results['player_stats_web']:
                if player['team'] == results['home_team']['id']:
                    home_players.append(player)
                elif player['team'] == results['away_team']['id']:
                    away_players.append(player)
        
        # Sort players by position: QB, RB, WR, TE
        position_order = {'QB': 0, 'RB': 1, 'WR': 2, 'TE': 3}
        home_player_stats.sort(key=lambda p: position_order.get(p['position'], 99))
        away_player_stats.sort(key=lambda p: position_order.get(p['position'], 99))
        
        # Save results to file
        sim_engine.save_results(results, "single_game")
        
        return render_template('simulation/results.html', 
                              results=results)
    except Exception as e:
        flash(f"Error running simulation: {str(e)}", "error")
        return redirect(url_for('simulation.new_simulation'))

@simulation_bp.route('/multiple/new', methods=['GET'])
def new_multiple_simulation():
    """Show the new multiple simulation form"""
    teams = list(sim_engine.teams.keys()) if sim_engine.teams else []
    return render_template('simulation/multiple_setup.html', teams=teams)

@simulation_bp.route('/multiple/run', methods=['POST', 'GET'])
def run_multiple_simulations():
    """Run multiple simulations based on form data"""
    try:
        # Handle both POST and GET requests
        if request.method == 'POST':
            home_team_id = request.form.get('home_team')
            away_team_id = request.form.get('away_team')
            num_sims = int(request.form.get('num_sims', 1))
        else:  # GET request
            home_team_id = request.args.get('home_team')
            away_team_id = request.args.get('away_team')
            num_sims = int(request.args.get('num_sims', 1))
        
        # Validate inputs
        if not home_team_id or not away_team_id:
            flash("Please select both teams", "error")
            return redirect(url_for('simulation.new_multiple_simulation'))
            
        # Get team objects
        home_team = sim_engine.get_team(home_team_id)
        away_team = sim_engine.get_team(away_team_id)
        
        if not home_team or not away_team:
            flash("Invalid team selection", "error")
            return redirect(url_for('simulation.new_multiple_simulation'))
        
        # Run simulations
        results = sim_engine.run_multiple_simulations(home_team, away_team, num_sims=num_sims)
        
        # Process results for display
        all_players = []
        
        # Calculate team statistics for each game
        for game in results['games']:
            # Initialize team stats if not present
            if 'total_yards' not in game['home_team']:
                game['home_team']['total_yards'] = 0
                game['home_team']['passing_yards'] = 0
                game['home_team']['rushing_yards'] = 0
                game['home_team']['turnovers'] = 0
                
            if 'total_yards' not in game['away_team']:
                game['away_team']['total_yards'] = 0
                game['away_team']['passing_yards'] = 0
                game['away_team']['rushing_yards'] = 0
                game['away_team']['turnovers'] = 0
            
            # Calculate stats from player stats
            if 'player_stats' in game:
                for player_id, stats in game['player_stats'].items():
                    team_id = stats.get('team_id', '')
                    
                    # Calculate passing yards
                    pass_yards = stats.get('pass_yards', 0)
                    rush_yards = stats.get('rush_yards', 0)
                    interceptions = stats.get('interceptions', 0)
                    fumbles = stats.get('fumbles', 0)
                    
                    # Add to appropriate team stats
                    if team_id == home_team.id:
                        game['home_team']['passing_yards'] += pass_yards
                        game['home_team']['rushing_yards'] += rush_yards
                        game['home_team']['total_yards'] += (pass_yards + rush_yards)
                        game['home_team']['turnovers'] += (interceptions + fumbles)
                    elif team_id == away_team.id:
                        game['away_team']['passing_yards'] += pass_yards
                        game['away_team']['rushing_yards'] += rush_yards
                        game['away_team']['total_yards'] += (pass_yards + rush_yards)
                        game['away_team']['turnovers'] += (interceptions + fumbles)
        
        # Calculate average team statistics and add to summary
        if 'summary' in results and results['games']:
            # Initialize stats in summary
            results['summary']['home_team']['total_yards_avg'] = 0
            results['summary']['home_team']['passing_yards_avg'] = 0
            results['summary']['home_team']['rushing_yards_avg'] = 0
            results['summary']['home_team']['turnovers_avg'] = 0
            
            results['summary']['away_team']['total_yards_avg'] = 0
            results['summary']['away_team']['passing_yards_avg'] = 0
            results['summary']['away_team']['rushing_yards_avg'] = 0
            results['summary']['away_team']['turnovers_avg'] = 0
            
            # Calculate averages
            num_games = len(results['games'])
            if num_games > 0:
                home_total_yards = sum(game['home_team'].get('total_yards', 0) for game in results['games'])
                home_passing_yards = sum(game['home_team'].get('passing_yards', 0) for game in results['games'])
                home_rushing_yards = sum(game['home_team'].get('rushing_yards', 0) for game in results['games'])
                home_turnovers = sum(game['home_team'].get('turnovers', 0) for game in results['games'])
                
                away_total_yards = sum(game['away_team'].get('total_yards', 0) for game in results['games'])
                away_passing_yards = sum(game['away_team'].get('passing_yards', 0) for game in results['games'])
                away_rushing_yards = sum(game['away_team'].get('rushing_yards', 0) for game in results['games'])
                away_turnovers = sum(game['away_team'].get('turnovers', 0) for game in results['games'])
                
                # Set averages in summary
                results['summary']['home_team']['total_yards_avg'] = home_total_yards / num_games
                results['summary']['home_team']['passing_yards_avg'] = home_passing_yards / num_games
                results['summary']['home_team']['rushing_yards_avg'] = home_rushing_yards / num_games
                results['summary']['home_team']['turnovers_avg'] = home_turnovers / num_games
                
                results['summary']['away_team']['total_yards_avg'] = away_total_yards / num_games
                results['summary']['away_team']['passing_yards_avg'] = away_passing_yards / num_games
                results['summary']['away_team']['rushing_yards_avg'] = away_rushing_yards / num_games
                results['summary']['away_team']['turnovers_avg'] = away_turnovers / num_games
        
        # Debug: Print the structure of the first game to see how team stats are stored
        if results['games']:
            print("DEBUG: Game structure after calculating stats:")
            print(f"Home team stats: {results['games'][0]['home_team']}")
            print(f"Away team stats: {results['games'][0]['away_team']}")
            
            if 'summary' in results:
                print("DEBUG: Summary structure:")
                print(f"Home team summary: {results['summary']['home_team']}")
                print(f"Away team summary: {results['summary']['away_team']}")
        
        # Process player projections
        if 'summary' in results and 'player_projections' in results['summary']:
            for player_id, proj in results['summary']['player_projections'].items():
                # Skip players with no stats
                if not proj:
                    continue
                
                # Create player object for template
                player = {
                    'id': player_id,
                    'name': proj.get('player_name', 'Unknown'),
                    'position': proj.get('position', 'Unknown'),
                    'team': proj.get('team_id', 'Unknown'),
                    'team_id': proj.get('team_id', ''),
                    'stats': {
                        'fantasy_pts_avg': proj.get('fantasy_points_avg', 0),
                        'fantasy_pts_min': proj.get('fantasy_points_min', 0),
                        'fantasy_pts_max': proj.get('fantasy_points_max', 0),
                        'fantasy_pts_std': proj.get('fantasy_points_std_dev', 0),
                        'games': proj.get('games_played', 0)
                    }
                }
                
                # Calculate expected range (avg ± 1 std dev)
                avg_pts = proj.get('fantasy_points_avg', 0)
                std_dev = proj.get('fantasy_points_std_dev', 0)
                player['stats']['fantasy_pts_range_low'] = max(0, avg_pts - std_dev)
                player['stats']['fantasy_pts_range_high'] = avg_pts + std_dev
                
                # Add position-specific stats
                if proj.get('position') == 'QB':
                    player['stats'].update({
                        'pass_yards_avg': proj.get('pass_yards_avg', 0),
                        'pass_tds_avg': proj.get('pass_tds_avg', 0),
                        'interceptions_avg': proj.get('interceptions_avg', 0),
                        'rush_yards_avg': proj.get('rush_yards_avg', 0),
                        'rush_tds_avg': proj.get('rush_tds_avg', 0)
                    })
                elif proj.get('position') in ['RB', 'WR', 'TE']:
                    player['stats'].update({
                        'rush_yards_avg': proj.get('rush_yards_avg', 0),
                        'rush_tds_avg': proj.get('rush_tds_avg', 0),
                        'receiving_yards_avg': proj.get('receiving_yards_avg', 0),
                        'receiving_tds_avg': proj.get('receiving_tds_avg', 0),
                        'receptions_avg': proj.get('receptions_avg', 0)
                    })
                elif proj.get('position') in ['LB', 'DL', 'CB', 'S']:
                    player['stats'].update({
                        'tackles_avg': proj.get('tackles_avg', 0),
                        'sacks_avg': proj.get('sacks_avg', 0),
                        'interceptions_avg': proj.get('interceptions_avg', 0),
                        'forced_fumbles_avg': proj.get('forced_fumbles_avg', 0),
                        'fumble_recoveries_avg': proj.get('fumble_recoveries_avg', 0)
                    })
                
                all_players.append(player)
                
        # Sort players by fantasy points
        all_players.sort(key=lambda p: p['stats'].get('fantasy_pts_avg', 0), reverse=True)
        
        # Calculate average plays per game
        avg_plays = 0
        if 'games' in results and results['games']:
            avg_plays = sum(game.get('total_plays', 0) for game in results['games']) / len(results['games'])
        
        # Save results to file
        sim_engine.save_results(results, "multiple_games")
        
        return render_template('simulation/multiple_results.html',
                              results=results,
                              players=all_players,
                              avg_plays=round(avg_plays, 1))
    except Exception as e:
        flash(f"Error running simulations: {str(e)}", "error")
        return redirect(url_for('simulation.new_multiple_simulation'))

# Register the blueprint with the app
def init_app(app, engine):
    global sim_engine
    # Use the engine passed from app.py
    sim_engine = engine
    app.register_blueprint(simulation_bp, url_prefix='/simulation')