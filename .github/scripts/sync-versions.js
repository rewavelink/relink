const fs = require("fs");
const path = require("path");
const yaml = require("js-yaml");

module.exports = async ({ github, context, core }) => {
    try {
        const templatePath = path.resolve(".github/ISSUE_TEMPLATE/bug_report.yml");
        const dropdownId = "sonolink_version";

        core.info(`Fetching releases for ${context.repo.owner}/${context.repo.repo}...`);
        const releases = await github.rest.repos.listReleases({
            owner: context.repo.owner,
            repo: context.repo.repo,
            per_page: 10
        });

        const tags = releases.data.map(release => release.tag_name);

        if (tags.length === 0) {
            core.info(`No releases found to update dropdown.`);
            return;
        }

        if (!fs.existsSync(templatePath)) {
            core.setFailed(`Template file not found at ${templatePath}`);
            return;
        }

        const fileContent = fs.readFileSync(templatePath, "utf-8");
        const doc = yaml.load(fileContent);
        const versionField = doc.body.find(field => field.id === dropdownId);

        if (!versionField) {
            core.setFailed(`Could not find a field with id: ${dropdownId} in the YAML body.`);
            return;
        }

        versionField.attributes.options = tags;
        const updatedYaml = yaml.dump(doc, { indent: 2, lineWidth: -1 });
        
        fs.writeFileSync(templatePath, updatedYaml);

        core.setOutput("version_tags", tags.join(', '));
        core.info(`Successfully updated "${dropdownId}" with: ${tags.join(', ')}`);

    } catch (error) {
        core.error(error);
        core.setFailed(`Failed to sync versions: ${error.message}`);
    }
};
