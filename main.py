import sys 			# system arguments
import traceback	# exception handling
from typing import Set, Dict, Tuple
from queue import LifoQueue

EPSILON = "eps"

State = int

class DFA:
	def __init__(self, stateCount: int,
				 alphabet: Set[chr],
				 finalStates: Set[State],
				 delta: Dict[Tuple[State, chr], State]):
		self.stateCount = stateCount
		self.states = set(range(stateCount))
		self.alphabet = alphabet
		self.initialState = 0
		self.finalStates = finalStates
		self.delta = delta

	def __str__(self):
		result = str(self.stateCount) + "\n"

		result += " ".join(str(x) for x in sorted(self.finalStates)) + "\n"

		for (currState, char), destState in sorted(self.delta.items()):
			result += " ".join(str(x) for x in [currState, char, destState])
			result += "\n"

		return result


class NFA:
	def __init__(self, stateCount: int,
				 alphabet: Set[chr],
				 finalStates: Set[State],
				 delta: Dict[Tuple[State, chr], Set[State]]):
		self.stateCount = stateCount
		self.states = set(range(stateCount))
		self.alphabet = alphabet
		self.initialState = 0
		self.finalStates = finalStates
		self.delta = delta

	def initEpsilonClosures(self):
		self.epsilonClosures = {k : set() for k in self.states}

		currentPath = list()

		def dfs(currState: State):
			# we have reached this state, any previous state can reach it
			currEpsilonClosure = self.epsilonClosures[currState]

			alreadyVisited = len(currEpsilonClosure) is not 0

			# add self to epsilon closure
			currEpsilonClosure.add(currState)

			for pathState in currentPath:
				self.epsilonClosures[pathState].update(currEpsilonClosure)

			# already visited, update without continuing the DFS
			if alreadyVisited:
				return

			# move through epsilon-transitions
			nextStates = self.delta.get((currState, EPSILON))

			if nextStates is None:
				return

			# continue the DFS
			for nextState in nextStates:
				currentPath.append(currState)
				dfs(nextState)
				currentPath.pop()

		for state in self.states:
			dfs(state)


	def convertToDFA(self) -> DFA:
		self.initEpsilonClosures()

		multiStateToSimpleState = dict() # O(1) indexing
		simpleStateIndex = 0
		generatedDelta = dict()

		queue = [] # multi-states to be processed

		initialMultiState = frozenset(self.epsilonClosures[self.initialState])

		multiStateToSimpleState[initialMultiState] = simpleStateIndex
		simpleStateIndex += 1

		queue.append(initialMultiState)

		# process multi-states
		while queue:
			currMultiState = queue.pop(0)

			# for every possible non-epsilon transition
			for char in self.alphabet - {EPSILON}:
				newMultiState = set()

				# build the destination multi-state
				for currState in currMultiState:
					nextStates = self.delta.get((currState, char))

					if nextStates is None:
						continue

					# epsilon-close all results
					for nextState in nextStates:
						newMultiState.update(self.epsilonClosures[nextState])

				frozenMultiState = frozenset(newMultiState)

				generatedDelta[(currMultiState, char)] = frozenMultiState

				# process this multi-state in the future
				if frozenMultiState not in multiStateToSimpleState:
					queue.append(frozenMultiState)
					multiStateToSimpleState[frozenMultiState] = simpleStateIndex
					simpleStateIndex += 1

		# also update the transitions and final states
		dfaDelta = dict()
		dfaFinalStates = set()

		for (currMultiState, char), destMultiState in generatedDelta.items():
			sourceState = multiStateToSimpleState[currMultiState]
			destinationState = multiStateToSimpleState[destMultiState]

			dfaDelta[(sourceState, char)] = destinationState

			if not currMultiState.isdisjoint(self.finalStates):
				dfaFinalStates.add(sourceState)

			if not destMultiState.isdisjoint(self.finalStates):
				dfaFinalStates.add(destinationState)

		# construct the DFA
		dfaInstance = DFA(
			stateCount = len(multiStateToSimpleState),
			alphabet = self.alphabet - {EPSILON},
			finalStates = dfaFinalStates,
			delta = dfaDelta
		)

		return dfaInstance


# verify the command line arguments
def validateInput():
	argc = len(sys.argv)
	expected_argc = 3

	displayString = "Invalid argument count: " + str(argc) + ". "
	displayString += "Must be: " + str(expected_argc)

	assert argc == expected_argc, displayString

def main():
	validateInput()

	input_file = open(sys.argv[1], "r")
	output_file = open(sys.argv[2], "w")

	stateCount = int(input_file.readline().strip())
	finalStates = set(map(int, input_file.readline().strip().split(" ")))
	delta = dict()

	alphabet = set()

	for line in input_file:
		transition = line.strip().split(" ")

		state = int(transition[0])
		char = transition[1]

		alphabet.add(char)

		delta[(state, char)] = set(map(int, transition[2:]))

	nfaInstance = NFA(
		stateCount = stateCount,
		finalStates = finalStates,
		alphabet = alphabet,
		delta = delta
	)

	dfaInstance = nfaInstance.convertToDFA()

	output_file.write(str(dfaInstance))

	input_file.close()
	output_file.close()


if __name__ == '__main__':
	main()