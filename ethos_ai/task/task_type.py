from enum import Enum

class TaskType(Enum):
	SERVICE = "service"
	DREAM = "dream"
	TRAIN_ETHIC = "train_ethic"
	TRAIN_INDIVIDUAL = "train_individual"
	TRAIN_CLIM = "train_clim"
	STOP = "stop"
	START = "start"
	AUTONOM_LIVING = "autonom_living"
	ADVISED_LIVING = "advised_living"

	def __str__(self):
		return f"TaskType: {self.name}"

	def __repr__(self):
		return f"<TaskType: {self.name}>"

	def __eq__(self, other: 'TaskType') -> bool:
		return self.value == other.value

	def __hash__(self):
		return hash(self.value)