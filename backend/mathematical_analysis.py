"""
Mathematical Chess Analysis Module
Implements advanced mathematical concepts for deep chess position analysis
Based on game theory, probability, information theory, and statistical methods
"""

import chess
import math
from collections import defaultdict
import numpy as np


class MathematicalAnalyzer:
    """Provides mathematical insights for chess positions and moves"""
    
    def __init__(self):
        self.piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
    
    # ==================== GAME THEORY ====================
    
    def calculate_minimax_depth_estimate(self, board, cp_loss):
        """
        Estimate effective search depth based on move quality
        Uses minimax theorem concepts
        """
        legal_moves = len(list(board.legal_moves))
        branching_factor = legal_moves
        
        # Estimate depth based on move quality
        if cp_loss <= 10:
            estimated_depth = 20  # Excellent move suggests deep calculation
        elif cp_loss <= 25:
            estimated_depth = 15
        elif cp_loss <= 50:
            estimated_depth = 12
        elif cp_loss <= 100:
            estimated_depth = 8
        else:
            estimated_depth = 5  # Blunder suggests shallow calculation
        
        # Alpha-beta pruning efficiency estimate
        alpha_beta_efficiency = math.sqrt(branching_factor)
        effective_nodes = branching_factor ** estimated_depth / alpha_beta_efficiency
        
        return {
            'estimated_depth': estimated_depth,
            'branching_factor': branching_factor,
            'nodes_searched_estimate': int(effective_nodes),
            'alpha_beta_efficiency': round(alpha_beta_efficiency, 2)
        }
    
    # ==================== PROBABILITY THEORY ====================
    
    def calculate_win_probability(self, eval_cp):
        """
        Convert centipawn evaluation to win probability using logistic function
        Based on statistical analysis of millions of games
        """
        if eval_cp is None:
            return 0.5
        
        # Logistic function: P(win) = 1 / (1 + e^(-eval/400))
        # 400 is empirically derived from chess databases
        win_prob = 1 / (1 + math.exp(-eval_cp / 400))
        
        return round(win_prob, 4)
    
    def calculate_move_probability_distribution(self, board, best_move, played_move, cp_loss):
        """
        Estimate probability distribution of move selection
        Uses Bayesian inference concepts
        """
        legal_moves = list(board.legal_moves)
        total_moves = len(legal_moves)
        
        # Prior probability (uniform distribution)
        prior_prob = 1 / total_moves
        
        # Likelihood based on move quality (Bayesian update)
        if played_move == best_move:
            likelihood = 0.95  # High probability of selecting best move
        elif cp_loss <= 25:
            likelihood = 0.70  # Good move
        elif cp_loss <= 50:
            likelihood = 0.40  # Inaccuracy
        elif cp_loss <= 100:
            likelihood = 0.15  # Mistake
        else:
            likelihood = 0.05  # Blunder
        
        # Posterior probability (simplified Bayes)
        posterior_prob = likelihood * prior_prob
        
        return {
            'prior_probability': round(prior_prob, 4),
            'likelihood': likelihood,
            'posterior_probability': round(posterior_prob, 4),
            'move_rank_estimate': self._estimate_move_rank(cp_loss, total_moves)
        }
    
    def _estimate_move_rank(self, cp_loss, total_moves):
        """Estimate where this move ranks among all legal moves"""
        if cp_loss <= 10:
            return 1  # Best or near-best
        elif cp_loss <= 25:
            return min(3, total_moves)
        elif cp_loss <= 50:
            return min(5, total_moves)
        elif cp_loss <= 100:
            return min(10, total_moves)
        else:
            return min(total_moves, 20)
    
    # ==================== INFORMATION THEORY ====================
    
    def calculate_position_entropy(self, board):
        """
        Calculate Shannon entropy of position
        Measures position complexity and uncertainty
        H(X) = -Σ p(x) × log₂(p(x))
        """
        legal_moves = list(board.legal_moves)
        num_moves = len(legal_moves)
        
        if num_moves == 0:
            return 0.0
        
        # Assume uniform distribution for simplicity
        # In reality, moves have different probabilities
        prob = 1 / num_moves
        entropy = -num_moves * prob * math.log2(prob)
        
        # Normalize to 0-10 scale
        max_entropy = math.log2(218)  # Max legal moves in chess
        normalized_entropy = (entropy / max_entropy) * 10
        
        return {
            'entropy': round(entropy, 3),
            'normalized_entropy': round(normalized_entropy, 2),
            'complexity_rating': self._complexity_rating(normalized_entropy),
            'legal_moves_count': num_moves
        }
    
    def _complexity_rating(self, normalized_entropy):
        """Rate position complexity"""
        if normalized_entropy < 3:
            return "Simple"
        elif normalized_entropy < 5:
            return "Moderate"
        elif normalized_entropy < 7:
            return "Complex"
        else:
            return "Highly Complex"
    
    def calculate_information_gain(self, eval_before, eval_after, cp_loss):
        """
        Calculate information gained/lost from the move
        Measures how much the move clarified or confused the position
        """
        if eval_before is None or eval_after is None:
            return {'information_gain': 0, 'clarity': 'Unknown'}
        
        # Information gain based on evaluation change
        eval_change = abs(eval_after - eval_before)
        
        # Normalize to bits of information
        information_bits = math.log2(1 + eval_change / 100)
        
        # Determine if move clarified or confused position
        if cp_loss <= 10:
            clarity = "Clarifying"  # Good move simplifies winning path
        elif cp_loss <= 50:
            clarity = "Neutral"
        else:
            clarity = "Confusing"  # Bad move creates uncertainty
        
        return {
            'information_gain_bits': round(information_bits, 3),
            'evaluation_change': eval_change,
            'clarity': clarity
        }
    
    # ==================== STATISTICAL METHODS ====================
    
    def calculate_move_quality_score(self, cp_loss, phase, material_balance):
        """
        Statistical scoring of move quality
        Uses weighted regression-like approach
        """
        # Base score from centipawn loss
        base_score = max(0, 100 - cp_loss / 5)
        
        # Phase weight (endgame mistakes are more costly)
        phase_weight = {
            'opening': 0.9,
            'middlegame': 1.0,
            'endgame': 1.2
        }.get(phase, 1.0)
        
        # Material balance factor (mistakes in winning positions are worse)
        if material_balance > 300:  # Winning
            balance_weight = 1.1
        elif material_balance < -300:  # Losing
            balance_weight = 0.9
        else:
            balance_weight = 1.0
        
        final_score = base_score * phase_weight * balance_weight
        
        return {
            'quality_score': round(final_score, 2),
            'base_score': round(base_score, 2),
            'phase_weight': phase_weight,
            'balance_weight': balance_weight,
            'percentile': self._score_to_percentile(final_score)
        }
    
    def _score_to_percentile(self, score):
        """Convert quality score to percentile ranking"""
        if score >= 95:
            return "99th percentile (Grandmaster level)"
        elif score >= 90:
            return "95th percentile (Master level)"
        elif score >= 80:
            return "80th percentile (Expert level)"
        elif score >= 70:
            return "60th percentile (Intermediate)"
        else:
            return "Below 50th percentile (Beginner)"
    
    # ==================== TACTICAL ANALYSIS ====================
    
    def analyze_tactical_features(self, board):
        """
        Analyze tactical features of position
        Checks, captures, threats, piece activity
        """
        features = {
            'is_check': board.is_check(),
            'is_checkmate': board.is_checkmate(),
            'is_stalemate': board.is_stalemate(),
            'can_capture': False,
            'num_attackers': 0,
            'num_defenders': 0,
            'center_control': 0,
            'king_safety': 0
        }
        
        # Check for captures
        for move in board.legal_moves:
            if board.is_capture(move):
                features['can_capture'] = True
                break
        
        # Count attackers and defenders (simplified)
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        for square in center_squares:
            attackers = board.attackers(board.turn, square)
            features['num_attackers'] += len(attackers)
            features['center_control'] += len(attackers)
        
        # King safety (number of pieces near king)
        king_square = board.king(board.turn)
        if king_square:
            king_zone = [
                king_square + 1, king_square - 1,
                king_square + 8, king_square - 8,
                king_square + 9, king_square - 9,
                king_square + 7, king_square - 7
            ]
            for sq in king_zone:
                if 0 <= sq < 64 and board.piece_at(sq):
                    features['king_safety'] += 1
        
        return features
    
    def calculate_material_balance(self, board):
        """Calculate material balance in centipawns"""
        white_material = 0
        black_material = 0
        
        for piece_type, value in self.piece_values.items():
            white_material += len(board.pieces(piece_type, chess.WHITE)) * value * 100
            black_material += len(board.pieces(piece_type, chess.BLACK)) * value * 100
        
        return white_material - black_material
    
    # ==================== COMPREHENSIVE ANALYSIS ====================
    
    def analyze_move_comprehensive(self, board, move, best_move, eval_before, eval_after, 
                                   cp_loss, phase):
        """
        Comprehensive mathematical analysis of a move
        Combines all mathematical frameworks
        """
        material_balance = self.calculate_material_balance(board)
        
        analysis = {
            # Game Theory
            'game_theory': self.calculate_minimax_depth_estimate(board, cp_loss),
            
            # Probability Theory
            'probability': {
                'win_prob_before': self.calculate_win_probability(eval_before),
                'win_prob_after': self.calculate_win_probability(eval_after),
                'win_prob_change': round(
                    self.calculate_win_probability(eval_after) - 
                    self.calculate_win_probability(eval_before), 4
                ),
                'move_distribution': self.calculate_move_probability_distribution(
                    board, best_move, move, cp_loss
                )
            },
            
            # Information Theory
            'information_theory': {
                'position_entropy': self.calculate_position_entropy(board),
                'information_gain': self.calculate_information_gain(
                    eval_before, eval_after, cp_loss
                )
            },
            
            # Statistical Analysis
            'statistics': self.calculate_move_quality_score(cp_loss, phase, material_balance),
            
            # Tactical Features
            'tactical': self.analyze_tactical_features(board),
            
            # Material
            'material_balance': material_balance
        }
        
        return analysis
    
    def generate_insights_text(self, analysis, move_san, best_move_san, cp_loss):
        """
        Generate human-readable insights from mathematical analysis
        """
        insights = []
        
        # Game Theory Insight
        gt = analysis['game_theory']
        insights.append(
            f"🎯 **Search Depth**: This move suggests calculation to depth ~{gt['estimated_depth']} "
            f"with {gt['branching_factor']} legal moves (branching factor). "
            f"Alpha-beta pruning would reduce search by ~{gt['alpha_beta_efficiency']}x."
        )
        
        # Probability Insight
        prob = analysis['probability']
        win_change = prob['win_prob_change'] * 100
        if win_change < -5:
            insights.append(
                f"📉 **Win Probability**: Dropped from {prob['win_prob_before']*100:.1f}% to "
                f"{prob['win_prob_after']*100:.1f}% ({win_change:+.1f}%). "
                f"This move significantly reduced your winning chances."
            )
        elif win_change > 5:
            insights.append(
                f"📈 **Win Probability**: Increased from {prob['win_prob_before']*100:.1f}% to "
                f"{prob['win_prob_after']*100:.1f}% ({win_change:+.1f}%). "
                f"Excellent move that improved your position!"
            )
        else:
            insights.append(
                f"➡️ **Win Probability**: {prob['win_prob_after']*100:.1f}% "
                f"(change: {win_change:+.1f}%). Position remains stable."
            )
        
        # Move Selection Probability
        move_dist = prob['move_distribution']
        insights.append(
            f"🎲 **Move Selection**: Estimated rank #{move_dist['move_rank_estimate']} among legal moves. "
            f"Bayesian likelihood: {move_dist['likelihood']*100:.0f}% (posterior: {move_dist['posterior_probability']*100:.1f}%)."
        )
        
        # Information Theory Insight
        entropy = analysis['information_theory']['position_entropy']
        info_gain = analysis['information_theory']['information_gain']
        insights.append(
            f"🧠 **Position Complexity**: {entropy['complexity_rating']} "
            f"(entropy: {entropy['normalized_entropy']}/10 with {entropy['legal_moves_count']} legal moves). "
            f"Move is {info_gain['clarity'].lower()} ({info_gain['information_gain_bits']:.2f} bits of information)."
        )
        
        # Statistical Quality
        stats = analysis['statistics']
        insights.append(
            f"📊 **Quality Score**: {stats['quality_score']:.1f}/100 "
            f"({stats['percentile']}). "
            f"Phase weight: {stats['phase_weight']}x, Balance weight: {stats['balance_weight']}x."
        )
        
        # Tactical Features
        tactical = analysis['tactical']
        tactical_notes = []
        if tactical['is_check']:
            tactical_notes.append("gives check")
        if tactical['can_capture']:
            tactical_notes.append("captures material")
        if tactical['center_control'] > 3:
            tactical_notes.append(f"controls center ({tactical['center_control']} attacks)")
        
        if tactical_notes:
            insights.append(f"⚔️ **Tactical**: This move {', '.join(tactical_notes)}.")
        
        # Material Balance
        mat_balance = analysis['material_balance']
        if abs(mat_balance) > 300:
            side = "White" if mat_balance > 0 else "Black"
            insights.append(
                f"♟️ **Material**: {side} is ahead by {abs(mat_balance)/100:.1f} pawns "
                f"({abs(mat_balance)} centipawns)."
            )
        
        return "\n\n".join(insights)


def analyze_position_mathematically(fen, move_uci, best_move_uci, eval_before, eval_after, 
                                   cp_loss, phase, move_san, best_move_san):
    """
    Main function to analyze a position with mathematical frameworks
    Returns comprehensive analysis and human-readable insights
    """
    board = chess.Board(fen)
    move = chess.Move.from_uci(move_uci) if move_uci else None
    best_move = chess.Move.from_uci(best_move_uci) if best_move_uci else None
    
    analyzer = MathematicalAnalyzer()
    
    # Get comprehensive analysis
    analysis = analyzer.analyze_move_comprehensive(
        board, move, best_move, eval_before, eval_after, cp_loss, phase
    )
    
    # Generate insights
    insights = analyzer.generate_insights_text(
        analysis, move_san, best_move_san, cp_loss
    )
    
    return {
        'analysis': analysis,
        'insights': insights,
        'summary': {
            'win_probability': analysis['probability']['win_prob_after'],
            'complexity': analysis['information_theory']['position_entropy']['complexity_rating'],
            'quality_score': analysis['statistics']['quality_score'],
            'estimated_depth': analysis['game_theory']['estimated_depth']
        }
    }
