
# SHIELD-RSU: Smart Hybrid Intersection Edge-based LLM Deployment for RoadSide Units

## Introduction

Salt Lake City (SLC) will host the 2034 Winter Olympic Games, substantially increasing traffic volume at key intersections. Due to urban density and limited space, traditional methods like expanding roads or intersections are neither feasible nor economically viable. Furthermore, current Roadside Units (RSUs), which provide reactive safety alerts based on zone occupancy thresholds, lack proactive, personalized, and predictive capabilities essential for safeguarding pedestrians, cyclists, and drivers during such high-demand events.

The proposed **SHIELD-RSU** (**Smart Hybrid Intersection Edge-based LLM Deployment for RoadSide Units**) addresses these challenges by leveraging real-time, lightweight Large Language Model (LLM) inference directly at the roadside, significantly enhancing intersection safety.

## Method Overview

### System Workflow

- **Input**: 
  - Ego vehicle transmits real-time data to RSU:
    - Location
    - Speed
    - Heading
  - RSU leverages real-time LiDAR-based perception data (objects already detected and classified).

- **LLM-based Prediction**:
  - RSU's lightweight edge-based LLM predicts trajectories and collision risks for nearby vehicles and vulnerable road users (VRUs).
  - Risk severity is quantified and ranked based on:
    - Time-to-collision (TTC)
    - Relative speed/distance
    - Trajectory overlap
    - VRU vulnerability index

- **Output**:
  - RSU generates personalized predictive Basic Safety Messages (BSMs), sending these back to the ego vehicle.
  - If a severe risk is detected, the RSU proactively initiates a traffic signal change (e.g., green to yellow/red) to mitigate the collision risk.

## Comparison: Aggregation Alert vs. SHIELD-RSU

| Feature | Aggregation Alert (Ouster Gemini) | **SHIELD-RSU (Proposed)** |
|--------|-------------------------------|----------------------------|
| **Trigger Mechanism** | Zone occupancy threshold | Context-aware TTC and trajectory prediction |
| **Risk Detection Granularity** | Zone-level | Object-level (individual vehicles/VRUs) |
| **Personalized Awareness** | Not supported | Personalized alerts using vehicle location, speed, and heading |
| **Predictive Capability** | None – reactive only | Predictive inference via Edge-based LLM |
| **Severity Ranking** | Fixed severity labels (e.g., WARNING) | Ranked by TTC, relative dynamics, VRU vulnerability |
| **Signal Control Integration** | Not supported | Adaptive signal phase control (e.g., yellow/red override) |
| **Adaptive to Traffic Patterns** | No trend analysis | Future extension supports behavior learning from LLM |
| **Communication Format** | Basic text message | Structured safety message + ranked objects + control actions |
| **Application Scope** | Monitoring only | Driver/CAV assistance + intersection control |

## What Makes a Good SHIELD-RSU Alert Message?

A good SHIELD-RSU alert message must be:

- **Personalized**: Tailored specifically to the receiving vehicle’s situation.
- **Context-rich**: Includes position, speed, type, and heading of identified threats.
- **Severity-ranked**: Clearly prioritizes threats based on quantified severity.
- **Action-oriented**: Clearly suggests recommended actions (e.g., slow down, stop).
- **Timely**: Sent early enough to enable safe and effective response.

### Example of SHIELD-RSU Alert Message (JSON):

```json
{
  "alert_type": "Collision Risk",
  "timestamp": 1732083745000000,
  "ego_vehicle": {
    "id": "EV123",
    "location": {"x": 12.5, "y": 38.2},
    "speed_mps": 11.4,
    "heading_deg": 82.3
  },
  "threat_entities": [
    {
      "id": "OBJ456",
      "type": "VRU - Pedestrian",
      "position": {"x": 13.1, "y": 38.5},
      "speed_mps": 1.2,
      "heading_deg": 270,
      "TTC_sec": 1.3,
      "severity_score": 0.92
    },
    {
      "id": "OBJ789",
      "type": "Vehicle",
      "position": {"x": 11.8, "y": 37.9},
      "speed_mps": 9.0,
      "heading_deg": 85,
      "TTC_sec": 2.7,
      "severity_score": 0.74
    }
  ],
  "recommended_action": "Initiate yellow-to-red signal change in eastbound lane. Notify vehicle: 'High collision risk with pedestrian at crosswalk. Prepare to stop.'"
}
```

## Applications and Benefits

- **Driver Assistance**: Personalized and predictive alerts improve drivers' reaction times and situational awareness.
- **Connected and Autonomous Vehicles (CAVs)**: Provides essential predictive context to enhance autonomous vehicle decision-making at busy intersections.
- **Enhanced VRU Safety**: Prioritizes and actively protects vulnerable road users, significantly reducing potential injuries.
- **Improved Intersection Throughput**: Optimizes intersection management during peak Olympic event traffic, reducing delays and potential conflicts.

## Conclusion

The **SHIELD-RSU** method represents a significant advancement over existing RSU capabilities. By integrating real-time predictive LLM analytics directly at the roadside, SHIELD-RSU proactively addresses intersection collision risks and enhances the safety of pedestrians, cyclists, and drivers during high-traffic scenarios such as the 2034 Winter Olympic Games.
