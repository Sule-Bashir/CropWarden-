from flask import Flask, render_template, request, jsonify, send_file
import random
import time
import json
import math
from datetime import datetime
import io
import os
import threading

app = Flask(__name__)

# ============================================
# ADVANCED ROBOT STATE MANAGEMENT
# ============================================
robot_state = {
    'position': {'x': 0, 'y': 0},
    'battery': 100,
    'status': 'idle',
    'mode': 'manual',
    'speed': 50,
    'direction': 'stopped',
    'grid_size': 5,
    'survey_progress': 0,
    'total_cells_scanned': 0,
    'start_time': datetime.now().isoformat(),
    'errors': [],
    'temperature': 45,  # Motor temperature
    'signal_strength': 98
}

# ============================================
# INTELLIGENT FIELD DATA GENERATION
# ============================================
def generate_field_data():
    """Creates realistic agricultural data with patterns"""
    field = []
    # Create a disease hotspot pattern
    hotspot_center = (random.randint(1, 3), random.randint(1, 3))

    for row in range(5):
        field_row = []
        for col in range(5):
            # Distance from hotspot affects disease probability
            distance = math.sqrt((row - hotspot_center[0])**2 + (col - hotspot_center[1])**2)

            # Base values with natural variation
            if distance < 1.5:
                # Near hotspot - high disease risk
                disease_base = random.uniform(65, 95)
                moisture_base = random.uniform(60, 85)  # Wet areas promote disease
                temp_base = random.uniform(22, 26)
            elif distance < 2.5:
                # Medium distance - moderate risk
                disease_base = random.uniform(30, 60)
                moisture_base = random.uniform(40, 65)
                temp_base = random.uniform(20, 28)
            else:
                # Far from hotspot - low risk
                disease_base = random.uniform(5, 25)
                moisture_base = random.uniform(25, 50)
                temp_base = random.uniform(18, 30)

            # Add some randomness
            disease = max(0, min(100, disease_base + random.uniform(-8, 8)))
            moisture = max(0, min(100, moisture_base + random.uniform(-10, 10)))
            temp = max(15, min(35, temp_base + random.uniform(-2, 2)))

            # Determine plant health
            if disease < 25:
                health = "excellent"
                health_color = "#28a745"
            elif disease < 50:
                health = "good"
                health_color = "#ffc107"
            elif disease < 75:
                health = "at_risk"
                health_color = "#fd7e14"
            else:
                health = "critical"
                health_color = "#dc3545"

            field_row.append({
                'row': row,
                'col': col,
                'soil_moisture': round(moisture, 1),
                'temperature': round(temp, 1),
                'disease_risk': round(disease, 1),
                'health_status': health,
                'health_color': health_color,
                'scanned': False,
                'scan_time': None,
                'notes': generate_plant_notes(health, disease)
            })
        field.append(field_row)
    return field

def generate_plant_notes(health, disease_risk):
    """Generate contextual notes for each plant"""
    if disease_risk > 75:
        notes = [
            "⚠️ Immediate action required",
            "Fungal infection detected",
            "Leaves showing spots",
            "Spread risk: HIGH"
        ]
    elif disease_risk > 50:
        notes = [
            "⚠️ Monitor closely",
            "Early signs of disease",
            "Consider preventive treatment",
            "Spread risk: MEDIUM"
        ]
    elif disease_risk > 25:
        notes = [
            "✅ Generally healthy",
            "Minor variations normal",
            "Continue regular monitoring",
            "Spread risk: LOW"
        ]
    else:
        notes = [
            "✅ Excellent condition",
            "Optimal growth",
            "No action needed",
            "Spread risk: NONE"
        ]
    return random.choice(notes)

field_grid = generate_field_data()

# ============================================
# ADVANCED AI DISEASE DETECTION ENGINE
# ============================================
class DiseaseDetectionAI:
    """Sophisticated AI model for plant disease analysis"""

    def __init__(self):
        self.disease_database = {
            'Early Blight': {
                'symptoms': ['Dark spots on leaves', 'Yellowing around spots', 'Target-like rings'],
                'treatment': 'Apply copper-based fungicide every 7-10 days. Remove infected leaves.',
                'severity': 'medium',
                'spread_rate': 'fast'
            },
            'Late Blight': {
                'symptoms': ['Water-soaked spots', 'White fungal growth', 'Rapid wilting'],
                'treatment': 'Immediate removal of infected plants. Apply chlorothalonil. Destroy crop residue.',
                'severity': 'high',
                'spread_rate': 'very_fast'
            },
            'Powdery Mildew': {
                'symptoms': ['White powdery patches', 'Distorted leaves', 'Reduced growth'],
                'treatment': 'Apply sulfur spray. Improve air circulation. Avoid overhead watering.',
                'severity': 'medium',
                'spread_rate': 'medium'
            },
            'Leaf Spot': {
                'symptoms': ['Small brown spots', 'Spots merge together', 'Leaves turn yellow'],
                'treatment': 'Remove affected leaves. Apply neem oil. Ensure proper spacing.',
                'severity': 'low',
                'spread_rate': 'slow'
            },
            'Rust': {
                'symptoms': ['Orange/brown pustules', 'Leaf distortion', 'Premature leaf drop'],
                'treatment': 'Apply fungicide. Remove plant debris. Choose resistant varieties.',
                'severity': 'medium',
                'spread_rate': 'medium'
            },
            'Healthy': {
                'symptoms': ['No visible symptoms', 'Vibrant green color', 'Normal growth'],
                'treatment': 'No treatment needed. Continue preventive care.',
                'severity': 'none',
                'spread_rate': 'none'
            }
        }

    def analyze(self, disease_risk, soil_moisture, temperature, location):
        """Comprehensive analysis combining multiple factors"""

        # Determine primary disease based on conditions
        if disease_risk > 70:
            if soil_moisture > 70 and temperature > 22:
                primary = 'Late Blight'
                confidence = min(95, disease_risk + random.uniform(5, 15))
            elif soil_moisture > 60:
                primary = 'Early Blight'
                confidence = min(90, disease_risk + random.uniform(0, 10))
            else:
                primary = 'Leaf Spot'
                confidence = min(85, disease_risk - random.uniform(5, 15))
        elif disease_risk > 40:
            if temperature > 25 and soil_moisture < 50:
                primary = 'Powdery Mildew'
                confidence = min(80, disease_risk + random.uniform(5, 15))
            elif temperature > 20:
                primary = 'Rust'
                confidence = min(75, disease_risk - random.uniform(0, 10))
            else:
                primary = 'Leaf Spot'
                confidence = min(70, disease_risk - random.uniform(10, 20))
        else:
            primary = 'Healthy'
            confidence = max(60, 100 - disease_risk * 1.5)

        # Get disease details
        disease_info = self.disease_database.get(primary, self.disease_database['Healthy'])

        # Generate recommendations
        recommendations = self.generate_recommendations(primary, disease_risk, soil_moisture)

        return {
            'primary_diagnosis': primary,
            'confidence': round(confidence, 1),
            'severity': disease_info['severity'],
            'spread_rate': disease_info['spread_rate'],
            'symptoms': disease_info['symptoms'],
            'treatment': disease_info['treatment'],
            'recommendations': recommendations,
            'environmental_factors': {
                'soil_moisture': soil_moisture,
                'temperature': temperature,
                'risk_level': self.get_risk_level(disease_risk)
            },
            'timestamp': datetime.now().isoformat()
        }

    def generate_recommendations(self, disease, risk, moisture):
        """Generate specific recommendations based on conditions"""
        recs = []

        if disease != 'Healthy':
            recs.append(f"Apply {disease} treatment immediately")
            recs.append("Isolate affected area to prevent spread")

            if moisture > 70:
                recs.append("⚠️ High moisture detected - reduce irrigation")
                recs.append("Improve drainage around plants")
            elif moisture < 30:
                recs.append("💧 Low moisture - increase irrigation")

            if risk > 80:
                recs.append("🚨 CRITICAL: Consider crop destruction in severe areas")
                recs.append("Contact agricultural extension officer")
        else:
            recs.append("✅ Continue regular monitoring")
            recs.append("Maintain current irrigation schedule")
            recs.append("Apply preventive treatment in 2 weeks")

        return recs

    def get_risk_level(self, risk):
        if risk < 25:
            return "Low"
        elif risk < 50:
            return "Moderate"
        elif risk < 75:
            return "High"
        else:
            return "Critical"

# Initialize AI
ai_engine = DiseaseDetectionAI()

# ============================================
# ANALYTICS ENGINE
# ============================================
class AnalyticsEngine:
    def __init__(self):
        self.scan_history = []
        self.alerts = []

    def add_scan(self, data):
        self.scan_history.append({
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'battery': robot_state['battery']
        })

        # Keep last 100 scans
        if len(self.scan_history) > 100:
            self.scan_history.pop(0)

    def get_statistics(self):
        if not self.scan_history:
            return {
                'total_scans': 0,
                'avg_disease': 0,
                'avg_moisture': 0,
                'critical_areas': 0,
                'healthy_areas': 0
            }

        total_scans = len(self.scan_history)
        avg_disease = sum(s['data'].get('disease_risk', 0) for s in self.scan_history) / total_scans
        avg_moisture = sum(s['data'].get('soil_moisture', 0) for s in self.scan_history) / total_scans
        critical = sum(1 for s in self.scan_history if s['data'].get('disease_risk', 0) > 70)
        healthy = sum(1 for s in self.scan_history if s['data'].get('disease_risk', 0) < 25)

        return {
            'total_scans': total_scans,
            'avg_disease': round(avg_disease, 1),
            'avg_moisture': round(avg_moisture, 1),
            'critical_areas': critical,
            'healthy_areas': healthy,
            'scan_frequency': f"{round(total_scans / max(1, (datetime.now() - datetime.fromisoformat(robot_state['start_time'])).total_seconds() / 3600), 1)}/hour"
        }

analytics = AnalyticsEngine()

# ============================================
# FLASK ROUTES
# ============================================
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/robot/status')
def robot_status():
    """Get current robot state"""
    return jsonify({
        **robot_state,
        'uptime': str(datetime.now() - datetime.fromisoformat(robot_state['start_time'])).split('.')[0]
    })

@app.route('/api/robot/control', methods=['POST'])
def robot_control():
    """Send commands to the robot"""
    global robot_state, field_grid

    command = request.json.get('command')
    value = request.json.get('value', None)

    if command == 'move':
        old_x, old_y = robot_state['position']['x'], robot_state['position']['y']
        robot_state['direction'] = value

        # Update position with boundaries
        if value == 'forward' and robot_state['position']['y'] < robot_state['grid_size'] - 1:
            robot_state['position']['y'] += 0.5
        elif value == 'backward' and robot_state['position']['y'] > 0:
            robot_state['position']['y'] -= 0.5
        elif value == 'left' and robot_state['position']['x'] > 0:
            robot_state['position']['x'] -= 0.5
        elif value == 'right' and robot_state['position']['x'] < robot_state['grid_size'] - 1:
            robot_state['position']['x'] += 0.5

        # Reduce battery based on movement
        if (old_x, old_y) != (robot_state['position']['x'], robot_state['position']['y']):
            robot_state['battery'] = max(0, robot_state['battery'] - 0.5)
            robot_state['motor_temperature'] = min(80, robot_state.get('motor_temperature', 45) + 0.2)

    elif command == 'stop':
        robot_state['direction'] = 'stopped'
        robot_state['motor_temperature'] = max(45, robot_state.get('motor_temperature', 45) - 0.1)

    elif command == 'mode':
        robot_state['mode'] = value

    elif command == 'scan':
        # Scan current cell
        x = min(4, max(0, int(round(robot_state['position']['x']))))
        y = min(4, max(0, int(round(robot_state['position']['y']))))

        if not field_grid[y][x]['scanned']:
            field_grid[y][x]['scanned'] = True
            field_grid[y][x]['scan_time'] = datetime.now().isoformat()
            robot_state['total_cells_scanned'] += 1

            # Add to analytics
            analytics.add_scan(field_grid[y][x])

            # Check for critical disease
            if field_grid[y][x]['disease_risk'] > 70:
                analytics.alerts.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'critical_disease',
                    'location': f"({x}, {y})",
                    'risk': field_grid[y][x]['disease_risk'],
                    'acknowledged': False
                })

    return jsonify({'success': True, 'robot': robot_state})

@app.route('/api/field/data')
def field_data():
    """Get field data"""
    return jsonify({
        'grid': field_grid,
        'robot': robot_state['position'],
        'stats': analytics.get_statistics(),
        'alerts': [a for a in analytics.alerts if not a.get('acknowledged', False)][-5:]
    })

@app.route('/api/sensor/current')
def current_sensor():
    """Get current sensor readings"""
    x = min(4, max(0, int(round(robot_state['position']['x']))))
    y = min(4, max(0, int(round(robot_state['position']['y']))))

    cell = field_grid[y][x]

    return jsonify({
        'soil_moisture': cell['soil_moisture'],
        'temperature': cell['temperature'],
        'disease_risk': cell['disease_risk'],
        'health_status': cell['health_status'],
        'position': {'x': x, 'y': y},
        'battery': robot_state['battery'],
        'scanned': cell['scanned'],
        'notes': cell['notes'],
        'motor_temp': round(robot_state.get('motor_temperature', 45), 1),
        'signal': robot_state['signal_strength']
    })

@app.route('/api/ai/analyze', methods=['POST'])
def ai_analyze():
    """Run AI analysis on current location"""
    x = min(4, max(0, int(round(robot_state['position']['x']))))
    y = min(4, max(0, int(round(robot_state['position']['y']))))

    cell = field_grid[y][x]

    # Run AI analysis
    analysis = ai_engine.analyze(
        disease_risk=cell['disease_risk'],
        soil_moisture=cell['soil_moisture'],
        temperature=cell['temperature'],
        location=(x, y)
    )

    # Add location info
    analysis['location'] = {'x': x, 'y': y}
    analysis['cell_data'] = cell

    return jsonify(analysis)

@app.route('/api/survey/start', methods=['POST'])
def start_survey():
    """Start autonomous survey"""
    global robot_state

    if robot_state['mode'] == 'auto':
        return jsonify({'success': False, 'message': 'Survey already running'})

    robot_state['mode'] = 'auto'
    robot_state['status'] = 'surveying'
    robot_state['survey_progress'] = 0

    def run_survey():
        global robot_state, field_grid
        cells = []

        # Create snake pattern for efficient scanning
        for y in range(5):
            if y % 2 == 0:
                for x in range(5):
                    cells.append((x, y))
            else:
                for x in range(4, -1, -1):
                    cells.append((x, y))

        for i, (x, y) in enumerate(cells):
            if robot_state['mode'] != 'auto':
                break

            # Move to cell
            robot_state['position'] = {'x': float(x), 'y': float(y)}
            robot_state['survey_progress'] = (i + 1) / 25 * 100
            robot_state['battery'] = max(0, robot_state['battery'] - 0.3)
            time.sleep(0.3)

            # Scan cell
            if not field_grid[y][x]['scanned']:
                field_grid[y][x]['scanned'] = True
                field_grid[y][x]['scan_time'] = datetime.now().isoformat()
                robot_state['total_cells_scanned'] += 1
                analytics.add_scan(field_grid[y][x])

        robot_state['mode'] = 'manual'
        robot_state['status'] = 'idle'
        robot_state['survey_progress'] = 100

    thread = threading.Thread(target=run_survey)
    thread.daemon = True
    thread.start()

    return jsonify({'success': True})

@app.route('/api/reset', methods=['POST'])
def reset_field():
    """Reset the entire field"""
    global field_grid, robot_state, analytics

    field_grid = generate_field_data()

    robot_state.update({
        'position': {'x': 0, 'y': 0},
        'battery': 100,
        'status': 'idle',
        'mode': 'manual',
        'direction': 'stopped',
        'survey_progress': 0,
        'total_cells_scanned': 0,
        'start_time': datetime.now().isoformat(),
        'motor_temperature': 45,
        'signal_strength': 98
    })

    analytics = AnalyticsEngine()

    return jsonify({'success': True})

@app.route('/api/alert/acknowledge', methods=['POST'])
def acknowledge_alert():
    """Acknowledge an alert"""
    alert_index = request.json.get('index')
    if 0 <= alert_index < len(analytics.alerts):
        analytics.alerts[alert_index]['acknowledged'] = True
    return jsonify({'success': True})

@app.route('/api/export/data')
def export_data():
    """Export scan data as JSON"""
    return jsonify({
        'robot': robot_state,
        'field': field_grid,
        'analytics': analytics.get_statistics(),
        'scans': analytics.scan_history,
        'export_time': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'robot': robot_state['status'],
        'battery': robot_state['battery']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
