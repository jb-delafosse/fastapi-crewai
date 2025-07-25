from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
import yaml
from pathlib import Path
from typing import List
from lumapps_poc.adapters.tools.human_tool import AskHumanTool
from lumapps_poc.infrastructure.run_context import RunContext

def load_config(file_path: str):
    """Load a YAML file."""
    with open(Path(__file__).parent / file_path, "r") as file:
        return yaml.safe_load(file)

class LumappsPoc():
    """LumappsPoc crew"""
    def __init__(self):
        self.agents_config = load_config('config/agents.yaml')
        self.tasks_config = load_config('config/tasks.yaml')

    def crew(self, run_context: RunContext) -> Crew:
        """Creates the LumappsPoc crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        ask_human_tool = AskHumanTool(run_context=run_context)

        researcher = Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            async_execution=True
        )
        analyst = Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            tools=[ask_human_tool],
            verbose=True,
            async_execution=True
        )

        research_task  = Task(
            description=self.tasks_config['research_task']['description'],
            expected_output=self.tasks_config['research_task']['expected_output'],
            agent=researcher,
            verbose=True
        )

        reporting_task = Task(
            description=self.tasks_config['reporting_task']['description'],
            expected_output=self.tasks_config['reporting_task']['expected_output'],
            agent=analyst,
            output_file='report.md',
        )

        return Crew(
            agents=[researcher, analyst],
            tasks=[research_task, reporting_task],
            process=Process.sequential,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
