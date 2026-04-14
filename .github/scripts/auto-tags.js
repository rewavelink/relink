module.exports = async ({ github, context, core }) => {
    const tags = {
        "Bug fix": "type: bugfix",
        "New feature": "idea: new feature",
        "Breaking change": "status: breaking change",
        "Refactor / internal cleanup": "type: refactor",
        "CI / dependency update": "area: dependencies",
        "Documentation update": "type: documentation",
    };
    const autoLabels = new Set(Object.values(tags));
    const pr = context.payload.pull_request;
    const prNumber = pr.number;
    const currentLabels = pr.labels ?? [];

    if (pr.locked) {
        core.info(`The PR #${prNumber} is locked, skipping autotag apply.`);
        return;
    }

    /** @type String */
    const prContent = (pr.body || '').trim();
    if (prContent.length === 0) {
        core.setFailed('There is no PR description.');
        return;
    };

    const match = prContent.match(
        /## Type of change([\s\S]*?)## Checklist/i
    );

    // This should not happpen as this job waits for the template vaildator
    // to return successfully.
    if (!match) {
        core.info('The Type of change section is not found.');
    };

    const section = match[1];
    const labels = [];

    for (const label of currentLabels) {
        if (autoLabels.has(label.name)) {
            await github.rest.issues.removeLabel({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: prNumber,
                name: label.name,
            });
        };
    };

    for (const [text, label] of Object.entries(tags)) {
        const regex = new RegExp(`- \\[x\\].*${text}`, 'i');
        if (regex.test(section)) {
            labels.push(label);
        };
    };

    if (labels.length === 0) {
        core.info('No labels need to be added.');
        return;
    };

    await github.rest.issues.addLabels({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: prNumber,
        labels: labels,
    });
};
