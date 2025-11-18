{
  "version": 1,
  "description": "StegVerse AutoPatch manifest – central rules for keeping StegTVC config files and related plumbing in sync across core repos.",
  "rules": [
    {
      "id": "tvc-config-sync",
      "description": "Ensure StegTVC config files exist and stay in sync across TVC and dependent repos.",
      "enabled": true,

      "targets": [
        {
          "repo": "StegVerse-Labs/TVC",
          "paths": [
            "TVC/data/stegtvc_config.json",
            "TVC/data/tv_config.json"
          ],
          "mode": "source-of-truth"
        },
        {
          "repo": "StegVerse-Labs/TV",
          "paths": [
            "TVC/data/stegtvc_config.json",
            "TVC/data/tv_config.json"
          ],
          "mode": "mirror"
        },
        {
          "repo": "StegVerse-Labs/hybrid-collab-bridge",
          "paths": [
            "TVC/data/stegtvc_config.json",
            "TVC/data/tv_config.json"
          ],
          "mode": "mirror"
        },
        {
          "repo": "StegVerse-Labs/StegVerse-SCW",
          "paths": [
            "TVC/data/stegtvc_config.json",
            "TVC/data/tv_config.json"
          ],
          "mode": "mirror"
        }
      ],

      "actions": [
        {
          "type": "ensure_files_exist",
          "from_source_repo": "StegVerse-Labs/TVC",
          "from_paths": [
            "TVC/data/stegtvc_config.json",
            "TVC/data/tv_config.json"
          ],
          "overwrite": false
        },
        {
          "type": "sync_contents",
          "source_repo": "StegVerse-Labs/TVC",
          "source_paths": [
            "TVC/data/stegtvc_config.json",
            "TVC/data/tv_config.json"
          ],
          "strategy": "canonical",
          "allow_create_pr": true,
          "pr_title_template": "AutoPatch: Sync TVC config files",
          "pr_labels": [
            "autopatch",
            "config-sync"
          ]
        }
      ],

      "conditions": {
        "apply_on": [
          "manual",
          "scheduled"
        ],
        "skip_if_open_pr_with_label": "autopatch:tvc-config-sync"
      },

      "metadata": {
        "owner": "StegVerse Core",
        "last_updated_by": "autogen",
        "notes": [
          "TVC is treated as the canonical source for StegVerse model routing and TV config.",
          "Other repos mirror the files into TVC/data/ so workflows can run locally in each repo."
        ]
      }
    }
  ]
}
