# Import necessary libraries
from opcua import Client
import paho.mqtt.client as mqtt
import time

# OPC UA client setup
opcua_url = "opc.tcp://10.213.120.105:4840"  # Replace with your OPC UA server URL
opcua_client = Client(opcua_url)

# OPC UA authentication
opcua_username = "OpcUaClient"  # Replace with your OPC UA username
opcua_password = "OpcUaClient"  # Replace with your OPC UA password
opcua_client.set_user(opcua_username)
opcua_client.set_password(opcua_password)

try:
    opcua_client.connect()
    print("______________________________OPCUA Client Connected Successfully________________________")
except Exception as e:
    print(f"Failed to connect to OPC UA server: {e}")
    exit(1)

# Lists of OPC UA node IDs and corresponding MQTT topics
opcua_node_ids = [
    "ns=2;s=/Bag/State/opMode",  
    "ns=2;s=/Channel/ChannelDiagnose/operatingTime",  
    "ns=2;s=/Channel/Diagnose/ipoCounter",
    "ns=2;s=/Channel/GeometricAxis/actProgPos[u1,1]",
    "ns=2;s=/Channel/GeometricAxis/actProgPos[u1,2]",
    "ns=2;s=/Channel/GeometricAxis/actProgPos[u1,3]",
    "ns=2;s=/Channel/GeometricAxis/actDistToGoEns[u1,1]",
    "ns=2;s=/Channel/GeometricAxis/actDistToGoEns[u1,2]",
    "ns=2;s=/Channel/GeometricAxis/actDistToGoEns[u1,3]",
    "ns=2;s=/Channel/MachineAxis/actFeedRate[u1,1]",
    "ns=2;s=/Channel/MachineAxis/actFeedRate[u1,1]",
    "ns=2;s=/Channel/MachineAxis/actFeedRate[u1,1]",
    "ns=2;s=/Channel/MachineAxis/cmdFeedRate",
    "ns=2;s=/Channel/GeometricAxis/feedRateOvr",
    "ns=2;s=/Channel/ChannelDiagnose/cycleTime",
    "ns=2;s=/Channel/LogicalSpindle/actSpeed",
    "ns=2;s=/Channel/LogicalSpindle/cmdSpeed",
    "ns=2;s=/Channel/LogicalSpindle/driveLoad",
    "ns=2;s=/Nck/ChannelDiagnose/poweronTime",
    "ns=2;s=/Channel/State/ncProgEndCounter",
    "ns=2;s=/Channel/ProgramInfo/actPartProgram",
    "ns=2;s=/Channel/ProgramInfo/actBlock",
    "ns=2;s=/Channel/State/actProgNetTime",
    "ns=2;s=/Channel/ProgramInfo/progName",
    "ns=2;s=/Bag/State/resetActive",
    "ns=2;s=/Bag/State/readyActive",
    "ns=2;s=/Channel/State/ncStartCounter",
    "ns=2;s=/Channel/State/ncResetCounter",
    "ns=2;s=/Channel/Spindle/driveLoad",
    "ns=2;s=/Channel/ProgramInfo/actLineNumber"
]

mqtt_topics = [
    "Machine Mode",   
    "Operating Time (in min)",      
    "Ipo Counter(/100 = in ms)",
    "X-axis position",
    "Y-axis position",
    "Z-axis position",
    "X-axis distance to go",
    "Y-axis distance to go",
    "Z-axis distance to go",
    "Actual feed rate x",
    "Actual feed rate y",
    "Actual feed rate z",
    "Command Feed rate",
    "Feed Rate Override",
    "Cycle Time",
    "Spindle RPM Actual",
    "Spindle RPM Command",
    "Spindle Load",
    "Power On Time(in Mins)",
    "No of parts",
    "Part Program",
    "actblock",
    "actProgramNetTime",
    "Program name",
    "resetActive",
    "readyActive",
    "ncStartCounter",
    "ncResetCounter",
    "driveLoad",
    "actLineNumber"
]

# Function to read data from OPC UA
def read_opcua_data(node_id):
    try:
        node = opcua_client.get_node(node_id)
        value = node.get_value()
        return value
    except Exception as e:
        print(f"Error reading from node {node_id}: {e}")
        return None

# Function to publish data to MQTT
def publish_mqtt_data(mqtt_client, topic, value):
    mqtt_client.publish(topic, value)
    print(f"Published '{value}' to topic '{topic}'")

# Initialize MQTT client
mqtt_client = mqtt.Client()

# Connect to MQTT broker
mqtt_broker = "localhost"  # Replace with your MQTT broker address
mqtt_port = 1883

try:
    mqtt_client.connect(mqtt_broker, mqtt_port)
except Exception as e:
    print(f"Failed to connect to MQTT broker: {e}")
    exit(1)  # Exit the script if connection fails

# Loop to read data from OPC UA and publish to MQTT broker every 1 second
try:
    while True:
        for node_id, topic in zip(opcua_node_ids, mqtt_topics):
            sensor_value = read_opcua_data(node_id)
            if sensor_value is not None:  # Ensure the value is not None before publishing
                publish_mqtt_data(mqtt_client, topic, sensor_value)
        time.sleep(1)  # Delay before the next read cycle
except KeyboardInterrupt:
    print("Stopping OPC UA to MQTT bridge...")
finally:
    # Disconnect both clients
    mqtt_client.disconnect()
    opcua_client.disconnect()
    print("Disconnected from MQTT broker and OPC UA server.")
