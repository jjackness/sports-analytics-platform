from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from simulation.engine import SimulationEngine

# Define the blueprint for simulation routes
simulation_bp = Blueprint('simulation', __name__)

# Initialize the simulation engine
sim_engine = SimulationEngine(output_dir="results")

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
        
        # Process player stats for display
        home_players = []
        away_players = []
        
        # Check for web-formatted player stats
        if 'player_stats_web' in results:
            for player in results['player_stats_web']:
                if player['team'] == results['home_team']['id']:
                    home_players.append(player)
                elif player['team'] == results['away_team']['id']:
                    away_players.append(player)
        
        # Sort players by position: QB, RB, WR, TE
        position_order = {'QB': 0, 'RB': 1, 'WR': 2, 'TE': 3}
        home_players.sort(key=lambda p: position_order.get(p['position'], 99))
        away_players.sort(key=lambda p: position_order.get(p['position'], 99))
        
        # Save results to file
        sim_engine.save_results(results, "single_game")
        
        return render_template('simulation/results.html', 
                              results=results, 
                              home_players=home_players,
                              away_players=away_players)
    except Exception as e:
        flash(f"Error running simulation: {str(e)}", "error")
        return redirect(url_for('simulation.new_simulation'))

@simulation_bp.route('/multiple/new', methods=['GET'])
def new_multiple_simulation():
    """Show the new multiple simulation form"""
    teams = list(sim_engine.teams.keys()) if sim_engine.teams else []
    return render_template('simulation/multiple_setup.html', teams=teams)

@simulation_bp.route('/multiple/run', methods=['POST'])
def run_multiple_simulations():
    """Run multiple simulations based on form data"""
    try:
        home_team_id = request.form.get('home_team')
        away_team_id = request.form.get('away_team')
        num_sims = int(request.form.get('num_sims', 1))
        
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
        
        # Process player stats
        all_players = []
        
        # Check for web-formatted player stats in summary
        if 'summary' in results and 'player_projections' in results['summary']:
            # Convert player projections to web format
            for player_id, proj in results['summary']['player_projections'].items():
                player = {
                    'id': player_id,
                    'name': proj.get('player_name', 'Unknown'),
                    'team': proj.get('team_id', ''),
                    'position': proj.get('position', ''),
                    'stats': {
                        'fantasy_pts_avg': proj.get('fantasy_points_avg', 0),
                        'fantasy_pts_min': proj.get('fantasy_points_min', 0),
                        'fantasy_pts_max': proj.get('fantasy_points_max', 0),
                        'fantasy_pts_std': proj.get('fantasy_points_std_dev', 0)
                    }
                }
                
                # Add position-specific stats
                if proj.get('position') == 'QB':
                    player['stats'].update({
                        'pass_att_avg': proj.get('pass_attempts_avg', 0),
                        'pass_comp_avg': proj.get('pass_completions_avg', 0),
                        'pass_yds_avg': proj.get('pass_yards_avg', 0),
                        'pass_tds_avg': proj.get('pass_tds_avg', 0)
                    })
                elif proj.get('position') == 'RB':
                    player['stats'].update({
                        'rush_att_avg': proj.get('rush_attempts_avg', 0),
                        'rush_yds_avg': proj.get('rush_yards_avg', 0),
                        'rush_tds_avg': proj.get('rush_tds_avg', 0)
                    })
                elif proj.get('position') in ['WR', 'TE']:
                    player['stats'].update({
                        'rec_avg': proj.get('receptions_avg', 0),
                        'rec_yds_avg': proj.get('receiving_yards_avg', 0),
                        'rec_tds_avg': proj.get('receiving_tds_avg', 0)
                    })
                
                all_players.append(player)
                
        # Sort players by fantasy points
        all_players.sort(key=lambda p: p['stats'].get('fantasy_pts_avg', 0), reverse=True)
        
        # Save results to file
        sim_engine.save_results(results, "multiple_games")
        
        return render_template('simulation/multiple_results.html',
                              results=results,
                              players=all_players)
    except Exception as e:
        flash(f"Error running simulations: {str(e)}", "error")
        return redirect(url_for('simulation.new_multiple_simulation'))

# Register the blueprint with the app
def init_app(app):
    app.register_blueprint(simulation_bp, url_prefix='/simulation')