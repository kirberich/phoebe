import json


class Device():
    """ The shared representation for a phoebe device, made to be compatible with the phoebe device db model
        on the cloud service.
    """

    def __init__(self, name, device_group, device_type, friendly_name='', data=None):
        self.name = name
        self.friendly_name = friendly_name
        self.device_group = device_group
        self.device_type = device_type
        self.data = data or {}

    @classmethod
    def from_json(cls, json_data):
        return cls(**json.loads(json_data))

    def to_dict(self):
        return {
            'name': self.name,
            'friendly_name': self.friendly_name,
            'device_group': self.device_group,
            'device_type': self.device_type,
            'data': self.data
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()
