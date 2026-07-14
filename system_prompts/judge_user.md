<question>
{task_description}
</question>

<agent_conversation>
{transcript}
</agent_conversation>

<output_files>
{output_files}
</output_files>

RUBRIC ({n_criteria} criteria — produce one verdict per item, in this order):
{rubrics_block}

Now produce the <judgment>...</judgment> block with exactly {n_criteria} verdicts in the format specified by the system prompt.
