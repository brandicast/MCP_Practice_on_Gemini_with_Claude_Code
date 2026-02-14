
module.exports = {
    database: {},
    mapping_table: {
        philio: {
            function_type: {
                0: "N/A",
                11: "Temperature Sensor",
                12: "Illumination Sensor",
                13: "Door / Window Sensor",
                14: "PIR Sensor",
                15: "Humidity Sensor",
                16: "GPIO",
                17: "Smoke Sensor",
                18: "CO Sensor",
                19: "CO2 Sensor",
                20: "Flood Sensor",
                21: "Glass Break Sensor",
                22: "Meter Switch",
                23: "Switch",
                24: "Dimmer",
                25: "Siren",
                26: "Curtain",
                27: "Remote",
                28: "Button",
                29: "Meter Sensor",
                30: "Meter Dimmer",
                31: "Door Lock",
                32: "Thermostat Fan",
                33: "Thermostat Mode",
                34: "Thermostat Temperature",
                35: "Remote Control",
                36: "Valve Switch",
                37: "Air Sensor",
                40: "UV Sensor",
                41: "Color Dimmer",
                42: "Sunrise(PS)",
                43: "Sunset(PS)",
                44: "Scene Status",
                45: "Door Lock Sensor",
                46: "Timer",
                49: "Heat Sensor",
                50: "Keypad",
                51: "PM Sensor",
                52: "Gas Meter",
                100: "Repeater"
            },
            productCode: {
                "00000000": {
                    name: "N/A",
                    img: "https://www.z-wave.com/logo.svg"
                },
                "01010000": {
                    name: "Philio All Switch",
                    img: "https://www.z-wave.com/logo.svg"
                },
                "01010001":{
                    name : "Philio Sun Rise",
                    img:"https://photos.app.goo.gl/YmRVqa7MyAgQ1wHt5"
                },
                "01010002":{
                    name : "Philio Sun Set",
                    img:"https://photos.app.goo.gl/YmRVqa7MyAgQ1wHt5"
                },
                "01010003":{
                    name:"Philio Scene Status",
                    img:"https://images.squarespace-cdn.com/content/v1/5c1afbd1266c07479bc41525/7d5ad760-51d2-40c8-8539-73278e67684a/philio-logo03.png?format=1500w"
                },
                "01010004":{
                    name:"Philio Timer",
                    img:"https://images.squarespace-cdn.com/content/v1/5c1afbd1266c07479bc41525/7d5ad760-51d2-40c8-8539-73278e67684a/philio-logo03.png?format=1500w"
                },
                "0101020C": {
                    name: "Philio PST02-A 4 in 1 Multi-Sensor",
                    img: "https://images.squarespace-cdn.com/content/v1/5c1afbd1266c07479bc41525/1546915375772-G6YTQXMOHXN5G92J1BD9/image-asset.png?format=500w"
                },
                "0101020D": {
                    name: "Philio PST02-B PIR Motion Sensor",
                    img: "https://images.squarespace-cdn.com/content/v1/5c1afbd1266c07479bc41525/1546915477802-2ELQ5HKTWF91RMZU59RR/PST02-B01.jpg?format=500w"
                },
                "0101020E": {
                    name: "Philio PST02-C Door/Window Contact Detector",
                    img: "https://images.squarespace-cdn.com/content/v1/5c1afbd1266c07479bc41525/1546915689112-6QJK5CDWKKM6KBGQMPNX/PST02-A%26C01.jpg?format=500w"
                },
                "01010003": {
                    name: "Philio Scene Status",
                    img: "https://www.z-wave.com/logo.svg"
                },
                "0101010F":{
                    name: "Philio PAN03 Switch Module",
                    img: "https://images.squarespace-cdn.com/content/v1/5c1afbd1266c07479bc41525/1547439735527-4B00C48V1A1KBR731WPX/PAN0302.jpg?format=500w"
                },
                "01010128": {
                    name: "Philio PAN15 Smart Energy Plug-in Switch",
                    img: "https://images.squarespace-cdn.com/content/v1/5c1afbd1266c07479bc41525/1546936444690-5MCB3CDXQKH8J7CPU91S/PAN15-0101.png?format=500w"
                },
                "FFFFFFFF": {
                    name: "Not Avaiable",
                    img: "https://www.z-wave.com/logo.svg"
                }
            },
            eventCode: {
                "1000": "Device Include or Exclude",
                "1001": "Found one device",
                "1002": "Device included",
                "1003": "Device removed",
                "1004": "Network updated OK",
                "1009": "System disarms",
                "1010": "System arm",
                "1011": "System partial arm 1",
                "1012": "System partial arm 2",
                "1013": "System partial arm 3",
                "1014": "System partial arm 4",
                "1015": "System partial arm 5",
                "1020": "System reset",
                "1030": "OTA_START",
                "1031": "OTA_STOP",
                "1032": "OTA_SUCCESS",
                "1033": "OTA_FAIL",
                "1034": "READ_EXTNVM_SUCCESS",
                "1035": "READ_EXTNVM_FAIL",
                "1036": "WRITE_EXTNVM_SUCCESS",
                "1037": "WRITE_EXTNVM_FAIL",
                "1040": "Device included",
                "4001": "Tamper trigger",
                "4002": "Low battery",
                "4003": "Battery Change",
                "4101": "PIR trigger",
                "4102": "Door/window open",
                "4103": "Door/window close",
                "4104": "Smoke trigger",
                "4105": "CO trigger",
                "4106": "CO2 trigger",
                "4107": "Flood trigger",
                "4108": "Glass break",
                "4109": "GPIO ON",
                "4110": "GPIO OFF",
                "4111": "Temperature over",
                "4112": "Temperature below",
                "4113": "Illumination over",
                "4114": "Illumination below",
                "4115": "Humidity over",
                "4116": "Humidity below",
                "4119": "Trigger OFF",
                "4120": "Power overload",
                "4121": "Meter changed",
                "4122": "Panic trigger",
                "4123": "Sonic trigger",
                "4128": "Heat trigger",
                "4129": "Heat trigger Off",
                "4130": "UnderHeat trigger",
                "4401": "Button 1 Down",
                "4402": "Button 2 Down",
                "4403": "Button 3 Down",
                "4404": "Button 4 Down",
                "4405": "Button 5 Down",
                "4406": "Button 6 Down",
                "4407": "Button 7 Down",
                "4408": "Button 8 Down",
                "4700": "Door lock Changed",
                "4701": "USERCODE_UPDATE",
                "4702": "USERCODE_OPEN",
                "4703": "USERCODE_CLOSE",
                "4801": "Temperature report",
                "4802": "Illumination report",
                "4803": "Humidity report",
                "4804": "Meter report",
                "4805": "CO2 report",
                "4806": "VOC report",
                "4807": "VOC report",
                "4808": "PM report",
                "4809": "Gas report",
                "4810": "Voltage report",
                "4811": "Current report",
                "4812": "PF report",
                "4813": "Water report",
                "4815": "Configuration SET",
                "5001": "Got control",
                "5002": "Status update",
                "5003": "CONFIG_CHANGE",
                "5004": "USERDATA_CHANGE",
                "5005": "BUILD_IN_SIREN_ON",
                "5006": "BUILD_IN_SIREN_OFF",
                "5007": "ZWAVE_INFO_UPDATE",
                "5008": "timer_v1_INFO_UPDATE",
                "5009": "timer_v1_INFO_UPDATE",
                "5031": "SET_MAP",
                "5032": "PUSH_MSG",
                "5102": "STATUS_UPDATE",
                "5010": "DEVICE WAKEUP",
                "9999": "ZWAVE_RUN_SWITCH",
            }
        }
    }
}