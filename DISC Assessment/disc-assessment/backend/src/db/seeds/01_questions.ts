import { Knex } from 'knex';

export async function seed(knex: Knex): Promise<void> {
  // Deletes ALL existing entries
  await knex('questions').del();

  // Insert seed questions
  await knex('questions').insert([
    {
      question_number: 1,
      scenario_text: "A critical server is down and multiple teams are affected. How do you approach this situation?",
      option_a: "Take immediate action and lead the recovery effort",
      option_b: "Call a meeting to discuss the issue with all stakeholders",
      option_c: "Follow established protocols and methodically work through the problem",
      option_d: "Analyze the logs and documentation to determine the root cause",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 2,
      scenario_text: "You've discovered a potential security vulnerability. What's your first step?",
      option_a: "Immediately implement a fix to address the vulnerability",
      option_b: "Notify your team and coordinate a response plan",
      option_c: "Document the issue thoroughly before taking action",
      option_d: "Research the vulnerability to understand its full implications",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 3,
      scenario_text: "A colleague has proposed a network redesign that you believe has flaws. How do you respond?",
      option_a: "Directly point out the flaws and propose your own solution",
      option_b: "Discuss your concerns in a team meeting to get everyone's input",
      option_c: "Suggest small improvements while maintaining the original concept",
      option_d: "Present a detailed analysis of the potential issues with supporting data",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 4,
      scenario_text: "You need to deploy a critical update during business hours. How do you proceed?",
      option_a: "Push the update immediately to fix the issue",
      option_b: "Contact all stakeholders to coordinate the best time",
      option_c: "Follow the standard change management process",
      option_d: "Create a detailed deployment plan with rollback procedures",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 5,
      scenario_text: "A user reports intermittent connectivity issues. What's your approach?",
      option_a: "Quickly implement the most likely solution",
      option_b: "Call the user to understand their experience better",
      option_c: "Methodically work through a standard troubleshooting process",
      option_d: "Analyze network logs and perform detailed diagnostics",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 6,
      scenario_text: "Your team needs to select a new monitoring tool. How do you contribute to this decision?",
      option_a: "Advocate strongly for the tool you believe is best",
      option_b: "Organize demonstrations from vendors to get everyone's input",
      option_c: "Support the team consensus even if it's not your first choice",
      option_d: "Create a detailed comparison matrix of all options",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 7,
      scenario_text: "A project deadline is at risk. What's your response?",
      option_a: "Take control and make decisive changes to get back on track",
      option_b: "Call a team meeting to boost morale and collaboration",
      option_c: "Continue working steadily and adapt to the new timeline",
      option_d: "Analyze what went wrong and create a detailed recovery plan",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 8,
      scenario_text: "A non-technical executive asks you to explain a complex technical issue. How do you respond?",
      option_a: "Give a direct, bottom-line explanation of the impact",
      option_b: "Use analogies and storytelling to make the concept relatable",
      option_c: "Patiently explain step-by-step at their level of understanding",
      option_d: "Provide a detailed explanation with supporting documentation",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 9,
      scenario_text: "Your team is implementing a new system. What aspect do you focus on most?",
      option_a: "Ensuring the implementation meets business objectives quickly",
      option_b: "Getting buy-in and enthusiasm from all users",
      option_c: "Ensuring stability and minimal disruption during the transition",
      option_d: "Ensuring all technical specifications and requirements are met",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 10,
      scenario_text: "How do you prefer to receive feedback on your work?",
      option_a: "Direct and straightforward, focused on results",
      option_b: "In an interactive conversation where I can share my thoughts",
      option_c: "Constructive and supportive, with specific examples",
      option_d: "Detailed and precise, with clear data points",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 11,
      scenario_text: "A routine maintenance task unexpectedly causes system issues. What's your first reaction?",
      option_a: "Take immediate action to restore service",
      option_b: "Communicate with affected users about the problem",
      option_c: "Follow the standard incident response protocol",
      option_d: "Investigate what went wrong before making changes",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 12,
      scenario_text: "Your workload has suddenly increased significantly. How do you handle it?",
      option_a: "Prioritize ruthlessly and delegate what you can",
      option_b: "Reach out to colleagues for collaboration and support",
      option_c: "Adjust your schedule and methodically work through tasks",
      option_d: "Analyze the situation and create a detailed work plan",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 13,
      scenario_text: "Your team has conflicting opinions on a technical approach. How do you contribute?",
      option_a: "Advocate strongly for the solution you believe is right",
      option_b: "Focus on building consensus and getting everyone's input",
      option_c: "Support compromise that maintains team harmony",
      option_d: "Analyze all options objectively with pros and cons",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 14,
      scenario_text: "A user repeatedly makes the same technical error despite your instructions. How do you respond?",
      option_a: "Directly explain what they're doing wrong and the correct procedure",
      option_b: "Arrange a personal demonstration to show them the correct way",
      option_c: "Patiently help them again, showing understanding for their frustration",
      option_d: "Create detailed step-by-step documentation for them to follow",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    },
    {
      question_number: 15,
      scenario_text: "What's most important to you when implementing a new technology?",
      option_a: "Speed of implementation and impact on business goals",
      option_b: "User adoption and enthusiasm for the new technology",
      option_c: "Minimal disruption and maintaining system stability",
      option_d: "Technical accuracy and adherence to best practices",
      dimension_a: "D",
      dimension_b: "I",
      dimension_c: "S",
      dimension_d: "C"
    }
  ]);
}