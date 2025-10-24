# © 2025 The Christman AI Project. All rights reserved.
#
# This code is released as part of a trauma-informed, dignity-first AI ecosystem
# designed to protect, empower, and elevate vulnerable populations.
#
# By using, modifying, or distributing this software, you agree to uphold the following:
# 1. Truth — No deception, no manipulation.
# 2. Dignity — Respect the autonomy and humanity of all users.
# 3. Protection — Never use this to exploit or harm vulnerable individuals.
# 4. Transparency — Disclose all modifications and contributions clearly.
# 5. No Erasure — Preserve the mission and ethical origin of this work.
#
# This is not just code. This is redemption in code.
# Contact: lumacognify@thechristmanaiproject.com
# https://thechristmanaiproject.com
import os
from PIL import Image, ImageDraw, ImageFont
import json

# Create directory for visuals
os.makedirs('screenshots', exist_ok=True)

# Base dimensions for all visuals
WIDTH = 1200
HEIGHT = 800
PADDING = 30
LINE_HEIGHT = 30
TITLE_FONT_SIZE = 48
SUBTITLE_FONT_SIZE = 32
BODY_FONT_SIZE = 24
FOOTER_FONT_SIZE = 18

# Colors
BACKGROUND_COLOR = (245, 247, 250)
TEXT_COLOR = (33, 33, 33)
HEADER_COLOR = (26, 115, 232)
BADGE_COLOR = (211, 47, 47)
SECTION_BG_COLOR = (255, 255, 255)
BORDER_COLOR = (220, 220, 220)
BUTTON_COLOR = (26, 115, 232)
CONFIDENCE_BG = (224, 224, 224)
CONFIDENCE_FG = (76, 175, 80)

# Intensity badge colors
INTENSITY_COLORS = {
    "mild": {"bg": (200, 230, 201), "fg": (56, 142, 60)},
    "moderate": {"bg": (255, 249, 196), "fg": (251, 192, 45)},
    "strong": {"bg": (255, 204, 188), "fg": (230, 74, 25)},
    "urgent": {"bg": (239, 154, 154), "fg": (198, 40, 40)}
}

def create_image(width, height, color=BACKGROUND_COLOR):
    """Create a new image with the given dimensions and color"""
    return Image.new('RGB', (width, height), color)

def draw_text(draw, text, position, font_size=BODY_FONT_SIZE, fill=TEXT_COLOR, 
              align="left", width=None, font_path=None):
    """Draw text with the specified parameters"""
    try:
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.load_default()
            # Scale default font
            font_size = int(font_size * 0.7)
    except IOError:
        font = ImageFont.load_default()
        # Scale default font
        font_size = int(font_size * 0.7)
    
    # Simple text wrapping
    if width:
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Estimate width with default font
            test_width = len(test_line) * (font_size * 0.6)
            
            if test_width <= width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        y = position[1]
        for line in lines:
            if align == "center":
                # Estimate width with default font
                line_width = len(line) * (font_size * 0.6)
                x = position[0] + (width - line_width) // 2
            else:
                x = position[0]
            
            draw.text((x, y), line, font=font, fill=fill)
            y += LINE_HEIGHT
        
        return y  # Return the new y position
    else:
        draw.text(position, text, font=font, fill=fill)
        return position[1] + LINE_HEIGHT

def draw_header(draw, title, subtitle=None):
    """Draw a header with title and optional subtitle"""
    y = PADDING
    
    # Title
    y = draw_text(draw, title, (PADDING, y), 
                  font_size=TITLE_FONT_SIZE, fill=HEADER_COLOR, 
                  align="center", width=WIDTH - 2*PADDING)
    y += 10
    
    # Subtitle
    if subtitle:
        y = draw_text(draw, subtitle, (PADDING, y), 
                      font_size=SUBTITLE_FONT_SIZE, fill=HEADER_COLOR, 
                      align="center", width=WIDTH - 2*PADDING)
    
    return y + 20  # Return the new y position with extra padding

def draw_section(draw, title, content, x, y, width, height, 
                 badge=None, badge_color=BADGE_COLOR):
    """Draw a section with title, content, and optional badge"""
    # Draw section background
    draw.rectangle([(x, y), (x + width, y + height)], 
                   fill=SECTION_BG_COLOR, outline=BORDER_COLOR)
    
    # Draw title
    section_y = y + PADDING
    
    # Draw badge if provided
    if badge:
        badge_width = len(badge) * (BODY_FONT_SIZE * 0.6) + 20
        badge_height = 30
        badge_x = x + width - badge_width - 10
        badge_y = y + 10
        
        draw.rectangle([(badge_x, badge_y), 
                        (badge_x + badge_width, badge_y + badge_height)], 
                       fill=badge_color, outline=badge_color)
        
        draw_text(draw, badge, 
                  (badge_x + 10, badge_y + 5), 
                  font_size=BODY_FONT_SIZE - 8, fill=(255, 255, 255))
    
    # Draw title
    section_y = draw_text(draw, title, (x + PADDING, section_y), 
                          font_size=SUBTITLE_FONT_SIZE, fill=TEXT_COLOR)
    section_y += 10
    
    # Draw content
    draw_text(draw, content, (x + PADDING, section_y), 
              font_size=BODY_FONT_SIZE, fill=TEXT_COLOR, 
              width=width - 2*PADDING)

def draw_button(draw, text, x, y, width=200, height=40, color=BUTTON_COLOR):
    """Draw a button with text"""
    draw.rectangle([(x, y), (x + width, y + height)], 
                   fill=color, outline=color)
    
    # Center text in button
    text_width = len(text) * (BODY_FONT_SIZE * 0.6)
    text_x = x + (width - text_width) // 2
    text_y = y + (height - BODY_FONT_SIZE) // 2
    
    draw_text(draw, text, (text_x, text_y), 
              font_size=BODY_FONT_SIZE, fill=(255, 255, 255))

def draw_confidence_meter(draw, x, y, width, confidence, height=10):
    """Draw a confidence meter with the given percentage"""
    # Background
    draw.rectangle([(x, y), (x + width, y + height)], 
                   fill=CONFIDENCE_BG, outline=CONFIDENCE_BG)
    
    # Foreground (confidence level)
    fill_width = int(width * confidence)
    draw.rectangle([(x, y), (x + fill_width, y + height)], 
                   fill=CONFIDENCE_FG, outline=CONFIDENCE_FG)

def draw_intensity_badge(draw, intensity, x, y, width=100, height=30):
    """Draw an intensity badge"""
    colors = INTENSITY_COLORS.get(intensity.lower(), 
                                 {"bg": (200, 200, 200), "fg": (100, 100, 100)})
    
    draw.rectangle([(x, y), (x + width, y + height)], 
                   fill=colors["bg"], outline=colors["bg"])
    
    # Center text in badge
    text_width = len(intensity) * (BODY_FONT_SIZE * 0.6)
    text_x = x + (width - text_width) // 2
    text_y = y + (height - BODY_FONT_SIZE) // 2
    
    draw_text(draw, intensity.capitalize(), (text_x, text_y), 
              font_size=BODY_FONT_SIZE - 4, fill=colors["fg"])

def draw_footer(draw, content):
    """Draw a footer at the bottom of the image"""
    footer_y = HEIGHT - PADDING - LINE_HEIGHT
    
    draw_text(draw, content, (PADDING, footer_y), 
              font_size=FOOTER_FONT_SIZE, fill=TEXT_COLOR, 
              align="center", width=WIDTH - 2*PADDING)

def create_multimodal_classifier_visual():
    """Create visual for the Multi-Modal Communication Classifier (Claims #1 & #3)"""
    img = create_image(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # Header
    y = draw_header(draw, "AlphaVox: Multi-Modal Communication Classifier", 
                    "Patent Claims #1 & #3 - USPTO Application Filed")
    
    # Main section
    section_width = WIDTH - 2*PADDING
    section_height = HEIGHT - y - 2*PADDING - 50  # Leave space for footer
    
    draw_section(draw, "Multi-Modal Classification", 
                "AlphaVox uses LSTM neural networks to analyze temporal sequences of gesture, audio, and gaze patterns. The classifier integrates real-time input from all modalities, performing synchronized interpretation within 35ms latency.", 
                PADDING, y, section_width, section_height, 
                badge="PATENT PENDING")
    
    # Subsection 1: Gesture Input
    subsection_width = (section_width - 3*PADDING) // 2
    subsection_height = 200
    subsection_y = y + PADDING + 100
    
    draw_section(draw, "Gesture Input", 
                "Hand movement patterns are tracked over time using LSTM neural networks. Temporal sequences capture nuanced patterns that simple snapshots cannot detect.", 
                PADDING*2, subsection_y, subsection_width, subsection_height)
    
    # Add buttons for gesture simulation
    button_y = subsection_y + subsection_height - 60
    draw_button(draw, "Simulate Hand Wave", PADDING*3, button_y)
    
    # Confidence results for gesture
    result_y = subsection_y + 100
    result_x = PADDING*2 + subsection_width + PADDING
    
    draw_section(draw, "Classification Results", 
                "Detected Expression: Hand Wave\nInterpreted Intent: Greeting\nGenerated Message: \"Hello there!\"\nConfidence: 92%", 
                result_x, subsection_y, subsection_width, subsection_height)
    
    # Add confidence meter
    meter_y = result_y + 120
    meter_x = result_x + PADDING
    meter_width = subsection_width - 2*PADDING
    
    draw_confidence_meter(draw, meter_x, meter_y, meter_width, 0.92)
    
    # Combined inputs section
    combined_y = subsection_y + subsection_height + PADDING
    
    draw_section(draw, "Multi-Modal Fusion", 
                "The true power of AlphaVox comes from combining multiple input modalities: gesture + vocalization + eye tracking. This multi-modal approach achieves 95% accuracy, compared to 82% for single-modality systems.", 
                PADDING*2, combined_y, section_width - 2*PADDING, 150)
    
    # Footer
    draw_footer(draw, "© 2025 The Christman AI Project - Chef Everett Christman - Patent Pending")
    
    # Save image
    img.save('screenshots/multimodal_classifier.png')
    print("Created multimodal classifier visual")

def create_adaptive_profile_visual():
    """Create visual for the Adaptive Profile System (Claims #2 & #5)"""
    img = create_image(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # Header
    y = draw_header(draw, "AlphaVox: Adaptive Profile System", 
                    "Patent Claims #2 & #5 - USPTO Application Filed")
    
    # Main section
    section_width = WIDTH - 2*PADDING
    section_height = HEIGHT - y - 2*PADDING - 50  # Leave space for footer
    
    draw_section(draw, "Adaptive Profile System", 
                "Each user has a profile that includes gesture-expression mappings, vocalization-intent mappings, and visual symbol libraries. These mappings are editable through a simple JSON interface and automatically load upon user login.", 
                PADDING, y, section_width, section_height, 
                badge="PATENT PENDING")
    
    # User profile selection
    profile_y = y + PADDING + 100
    profile_width = (section_width - 3*PADDING) // 2
    
    draw_section(draw, "User Profile", 
                "Select User: Alex (Autism, Non-verbal)", 
                PADDING*2, profile_y, profile_width, 60)
    
    # Expression mappings
    mapping_y = profile_y + 80
    
    draw_section(draw, "Expression Mappings", 
                "Personalized mappings between physical expressions and communication intent", 
                PADDING*2, mapping_y, profile_width, 250)
    
    # Add example mappings
    mapping_lines = [
        {"expression": "Hand Wave", "intent": "Greeting", "confidence": 0.92},
        {"expression": "Head Tilt", "intent": "Confusion", "confidence": 0.85},
        {"expression": "Extended Gaze Left", "intent": "Request Item", "confidence": 0.78},
        {"expression": "Prolonged Vowel Sound", "intent": "Excitement", "confidence": 0.88}
    ]
    
    mapping_start_y = mapping_y + 80
    for i, mapping in enumerate(mapping_lines):
        mapping_item_y = mapping_start_y + i * 40
        
        draw_text(draw, f"{mapping['expression']} → {mapping['intent']}", 
                  (PADDING*3, mapping_item_y), font_size=BODY_FONT_SIZE - 4)
        
        # Add confidence meter
        meter_y = mapping_item_y + 25
        meter_x = PADDING*3
        meter_width = profile_width - 3*PADDING
        
        draw_confidence_meter(draw, meter_x, meter_y, meter_width, mapping["confidence"])
    
    # Profile settings
    settings_x = PADDING*2 + profile_width + PADDING
    
    draw_section(draw, "Profile Settings", 
                "Voice Output Settings, Symbol System Preference, Learning Algorithm Sensitivity", 
                settings_x, profile_y, profile_width, 150)
    
    # Session memory
    memory_y = profile_y + 170
    
    draw_section(draw, "Session Memory", 
                "AlphaVox maintains a history of expressions and interpretations to improve future predictions and provide context awareness.", 
                settings_x, memory_y, profile_width, 160)
    
    # Add example session items
    memory_start_y = memory_y + 80
    memory_items = [
        "10:15 AM: Hand wave gesture detected → Greeting",
        "10:18 AM: Vocalization detected → Request help"
    ]
    
    for i, item in enumerate(memory_items):
        draw_text(draw, item, (settings_x + PADDING, memory_start_y + i * 30), 
                  font_size=BODY_FONT_SIZE - 6)
    
    # Footer
    draw_footer(draw, "© 2025 The Christman AI Project - Chef Everett Christman - Patent Pending")
    
    # Save image
    img.save('screenshots/adaptive_profile.png')
    print("Created adaptive profile visual")

def create_emotional_intensity_visual():
    """Create visual for the Emotional Intensity Scoring Engine (Claim #4)"""
    img = create_image(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # Header
    y = draw_header(draw, "AlphaVox: Emotional Intensity Scoring Engine", 
                    "Patent Claim #4 - USPTO Application Filed")
    
    # Main section
    section_width = WIDTH - 2*PADDING
    section_height = HEIGHT - y - 2*PADDING - 50  # Leave space for footer
    
    draw_section(draw, "Emotional Intensity Scoring Engine", 
                "The vocalization model includes amplitude and pitch normalization routines. Emotional states such as effort and distress are classified by comparing these features to historical baselines and assigning intensity labels such as 'mild', 'strong', or 'urgent'.", 
                PADDING, y, section_width, section_height, 
                badge="PATENT PENDING")
    
    # Feature extraction
    features_y = y + PADDING + 100
    features_width = (section_width - 3*PADDING) // 2
    
    draw_section(draw, "Vocalization Feature Extraction", 
                "AlphaVox extracts normalized audio features that capture emotional intensity:", 
                PADDING*2, features_y, features_width, 200)
    
    # Add example features
    features_start_y = features_y + 80
    features = [
        "Pitch Variation: 0.72",
        "Amplitude: 0.85",
        "Duration: 1.65s",
        "Spectral Centroid: 842.37Hz",
        "Harmonics Ratio: 0.78"
    ]
    
    for i, feature in enumerate(features):
        draw_text(draw, feature, (PADDING*3, features_start_y + i * 25), 
                  font_size=BODY_FONT_SIZE - 4)
    
    # Intensity classification
    intensity_x = PADDING*2 + features_width + PADDING
    
    draw_section(draw, "Intensity Classification", 
                "Emotional intensity is classified into four levels:", 
                intensity_x, features_y, features_width, 200)
    
    # Add intensity badges
    intensity_badges_y = features_y + 80
    intensities = ["mild", "moderate", "strong", "urgent"]
    
    for i, intensity in enumerate(intensities):
        badge_y = intensity_badges_y + i * 40
        draw_intensity_badge(draw, intensity, intensity_x + PADDING, badge_y, width=120)
    
    # Historical comparison
    historical_y = features_y + 220
    
    draw_section(draw, "Historical Baseline Comparison", 
                "Current vocalizations are compared to historical baselines, with significant deviations flagged as potentially urgent needs.", 
                PADDING*2, historical_y, section_width - 2*PADDING, 120)
    
    # Add comparison details
    comparison_y = historical_y + 70
    
    draw_text(draw, "User Baseline (30-day average): Pitch Variation: 0.33, Amplitude: 0.31", 
              (PADDING*3, comparison_y), font_size=BODY_FONT_SIZE - 4)
    
    draw_text(draw, "Current Sample Deviation: 157.2% above baseline", 
              (PADDING*3, comparison_y + 30), font_size=BODY_FONT_SIZE - 4)
    
    draw_text(draw, "Pattern Recognition: This expression shows significantly higher intensity than baseline, indicating urgent needs.", 
              (PADDING*3, comparison_y + 60), font_size=BODY_FONT_SIZE - 4)
    
    # Footer
    draw_footer(draw, "© 2025 The Christman AI Project - Chef Everett Christman - Patent Pending")
    
    # Save image
    img.save('screenshots/emotional_intensity.png')
    print("Created emotional intensity visual")

def create_offline_capability_visual():
    """Create visual for the Offline Deployable Framework (Claim #6)"""
    img = create_image(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # Header
    y = draw_header(draw, "AlphaVox: Offline Deployable Framework", 
                    "Patent Claim #6 - USPTO Application Filed")
    
    # Main section
    section_width = WIDTH - 2*PADDING
    section_height = HEIGHT - y - 2*PADDING - 50  # Leave space for footer
    
    draw_section(draw, "Offline Deployable Framework", 
                "AlphaVox can be deployed without requiring an internet connection. The system stores all language models, expression mappings, and learned user patterns locally, ensuring accessibility in all environments.", 
                PADDING, y, section_width, section_height, 
                badge="PATENT PENDING")
    
    # Local storage section
    storage_y = y + PADDING + 100
    col_width = (section_width - 3*PADDING) // 2
    
    draw_section(draw, "Local Storage Architecture", 
                "All critical components are stored on-device:", 
                PADDING*2, storage_y, col_width, 200)
    
    # Add storage components
    components_start_y = storage_y + 80
    components = [
        "LSTM Neural Network Models (42MB)",
        "User Profiles (5-10MB per user)",
        "Expression Mappings (2MB)",
        "Voice Synthesis Engine (85MB)",
        "Symbol Libraries (15MB)"
    ]
    
    for i, component in enumerate(components):
        draw_text(draw, component, (PADDING*3, components_start_y + i * 25), 
                  font_size=BODY_FONT_SIZE - 4)
    
    # Deployment options
    deploy_x = PADDING*2 + col_width + PADDING
    
    draw_section(draw, "Deployment Options", 
                "AlphaVox can be deployed in various environments:", 
                deploy_x, storage_y, col_width, 200)
    
    # Add deployment options
    deployment_start_y = storage_y + 80
    deployments = [
        "Mobile Device (iOS/Android)",
        "Standalone Tablet",
        "Desktop Application",
        "Specialized Hardware Device",
        "School/Clinic Network (LAN)"
    ]
    
    for i, deployment in enumerate(deployments):
        draw_text(draw, deployment, (deploy_x + PADDING, deployment_start_y + i * 25), 
                  font_size=BODY_FONT_SIZE - 4)
    
    # Sync capabilities
    sync_y = storage_y + 220
    
    draw_section(draw, "Optional Synchronization", 
                "While fully functional offline, AlphaVox can optionally synchronize data when internet becomes available, enabling backup and multi-device support without compromising core functionality.", 
                PADDING*2, sync_y, section_width - 2*PADDING, 120)
    
    # Footer
    draw_footer(draw, "© 2025 The Christman AI Project - Chef Everett Christman - Patent Pending")
    
    # Save image
    img.save('screenshots/offline_capability.png')
    print("Created offline capability visual")

def create_patent_summary_visual():
    """Create a summary visual for all patent claims"""
    img = create_image(WIDTH, HEIGHT)
    draw = ImageDraw.Draw(img)
    
    # Header
    y = draw_header(draw, "AlphaVox: Patent-Pending Technology", 
                    "USPTO Application Filed")
    
    # Introduction section
    section_width = WIDTH - 2*PADDING
    section_height = 100
    
    draw_section(draw, "Revolutionary AI Communication System", 
                "AlphaVox represents a breakthrough in assistive technology for nonverbal and neurodivergent individuals, with six distinct patent-pending technologies that work together to create an unparalleled communication solution.", 
                PADDING, y, section_width, section_height, 
                badge="PATENT PENDING")
    
    # Claims grid - 2x3 layout
    grid_y = y + section_height + PADDING
    cell_width = (section_width - 3*PADDING) // 2
    cell_height = 150
    
    # Claim 1
    draw_section(draw, "Claim #1: Multi-Modal Classification", 
                "LSTM-based neural networks that analyze temporal sequences of gesture, vocalization, and eye tracking inputs with synchronized interpretation.", 
                PADDING, grid_y, cell_width, cell_height)
    
    # Claim 2
    draw_section(draw, "Claim #2: Adaptive Profile System", 
                "User-specific mappings between physical expressions and communication intent, with personalized learning parameters.", 
                PADDING*2 + cell_width, grid_y, cell_width, cell_height)
    
    # Claim 3
    draw_section(draw, "Claim #3: Self-Improvement Architecture", 
                "System autonomously refines communication models based on user interactions, adjusting recognition thresholds and timing parameters.", 
                PADDING, grid_y + cell_height + PADDING, cell_width, cell_height)
    
    # Claim 4
    draw_section(draw, "Claim #4: Emotional Intensity Scoring", 
                "Vocalization models with amplitude and pitch normalization that classify emotional states and assign intensity labels.", 
                PADDING*2 + cell_width, grid_y + cell_height + PADDING, cell_width, cell_height)
    
    # Claim 5
    draw_section(draw, "Claim #5: Dynamic Symbol Substitution", 
                "Real-time association of gestures and vocalizations with preferred communication symbols and messages.", 
                PADDING, grid_y + 2*(cell_height + PADDING), cell_width, cell_height)
    
    # Claim 6
    draw_section(draw, "Claim #6: Offline Deployable Framework", 
                "Complete system functionality without internet connectivity, with all models and mappings stored locally.", 
                PADDING*2 + cell_width, grid_y + 2*(cell_height + PADDING), cell_width, cell_height)
    
    # Footer
    draw_footer(draw, "© 2025 The Christman AI Project - Chef Everett Christman - Patent Pending")
    
    # Save image
    img.save('screenshots/patent_summary.png')
    print("Created patent summary visual")

def main():
    """Generate all patent visualizations"""
    try:
        create_multimodal_classifier_visual()
        create_adaptive_profile_visual()
        create_emotional_intensity_visual()
        create_offline_capability_visual()
        create_patent_summary_visual()
        print("All patent visuals generated successfully in the 'screenshots' directory")
    except Exception as e:
        print(f"Error generating patent visuals: {e}")

if __name__ == "__main__":
    main()