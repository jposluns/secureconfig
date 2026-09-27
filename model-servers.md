---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "658738f0d91e92f38769f2ab4c15750ace4d2edea9ae5d80447859a667998a0f",
  "components": {
    "llama": {
      "name": "llama.cpp",
      "basis": "e0dff58475bc9ed68eedcb265ee998f2fcabb3b1",
      "sources": {
        "s808f8d1c8da9": "https://github.com/ggml-org/llama.cpp/blob/e0dff58475bc9ed68eedcb265ee998f2fcabb3b1/tools/server/README.md"
      }
    },
    "vllm": {
      "name": "vLLM",
      "basis": "v0.30.0",
      "sources": {
        "s65a60be2808c": "https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L140-L247",
        "s36fcb4c4fc18": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/serve/middleware/authenticate.py#L11-L62",
        "s90b2ada8e38b": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/cli_args.py#L256-L266",
        "sb9c63e342665": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/launcher.py#L211-L225",
        "s701a469f3c23": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/launcher.py#L270-L288",
        "se5660cf62498": "https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L109-L138",
        "sec32bab94990": "https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L3-L55",
        "s1de6a9f4ed49": "https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L442-L538",
        "sd18839fe8984": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/parallel_state.py#L1793-L1880",
        "s27ba1937dca0": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/utils.py#L467-L506",
        "s7abb84b61c6e": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/utils.py#L634-L647",
        "s1fc694d68aac": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/config/parallel.py#L100-L330",
        "s8c1221a0c7b9": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/config/parallel.py#L890-L960",
        "s15bf642ce14e": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/ray_executor_v2.py#L127-L139",
        "sfecabc3bc16d": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/engine/utils.py#L1039-L1084",
        "se3e528b9ca5c": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/engine/utils.py#L1130-L1247",
        "s8ddf90ed2cb1": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/engine/coordinator.py#L79-L97",
        "sb6a7effd4318": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/device_communicators/shm_broadcast.py#L519-L537",
        "s2dad806d290a": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/multiproc_executor.py#L148-L169",
        "s66d892167b5d": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/ray_executor_v2.py#L327-L336",
        "s19f4f6a6790f": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/cli/serve.py#L215-L253",
        "sdb9dac146cd4": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_scheduler.py#L299-L382",
        "s0ec5750d8161": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_scheduler.py#L75-L79",
        "s2c10a0015812": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/envs.py#L1650-L1680",
        "s97fe4257dfc6": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L1160-L1187",
        "s623327f195f8": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L1793-L1801",
        "s0341e26f43ae": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L2261-L2296",
        "s0fa9693f3666": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L948-L1035",
        "sd52612723dde": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/cli_args.py#L424-L429",
        "sb6766a13ce4a": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/grpc_server.py#L87-L118",
        "sbc83e9d09208": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/cli/serve.py#L145-L148",
        "s471a29420e3a": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/cli/serve.py#L85-L95",
        "s80888a79d6e2": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/dp_supervisor.py#L118-L132",
        "s7d70cef86248": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/dp_supervisor.py#L220-L238",
        "sd80aa5c7d7cc": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/dp_supervisor.py#L322-L349",
        "sdf64db690b1c": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/utils/network_utils.py#L34-L73",
        "s0497a5e3fe44": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/engine/arg_utils.py#L2310-L2336",
        "s92bab6d08b69": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/envs.py#L701-L715",
        "s7cb33671d83d": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/utils/network_utils.py#L166-L247",
        "scfeadcdcd9a1": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/envs.py#L1433-L1445",
        "s3b1ce10c3e66": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/parallel_state.py#L494-L508",
        "s67bc8be47a91": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/utils/network_utils.py#L135-L147",
        "sed65b4428b70": "https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/uniproc_executor.py#L77-L88"
      }
    },
    "vllm-a": {
      "name": "vLLM source",
      "basis": "dee37d89115db4c94a820a79a78a7828e141c910",
      "sources": {
        "s7b472d8bd2d0": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/cli_args.py#L304",
        "sd13651484ed1": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/serve/middleware/register.py#L32-L36",
        "safb9d5e38921": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/utils/argparse_utils.py#L329-L330",
        "sccd45a9ffb02": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/v1/utils.py#L210-L246",
        "sc14e6c37774c": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/v1/utils.py#L384-L411",
        "sba4bc217b9de": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/cli/serve.py#L63-L64",
        "scf43e725574b": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/serve/utils/api_utils.py#L271-L286",
        "s4b161060c056": "https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/grpc_server.py#L64"
      }
    },
    "vllm-b": {
      "name": "vLLM second source",
      "basis": "8c1557a79c539ffe82d004d2a0c8d7b5e71159ce",
      "sources": {
        "sdbf0512be177": "https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/entrypoints/launchers/cli_args.py#L296",
        "se5d922e084ed": "https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/envs.py#L801"
      }
    },
    "tgi": {
      "name": "TGI launcher/image",
      "basis": "v3.3.7",
      "sources": {
        "s6d442de48f37": "https://github.com/huggingface/text-generation-inference/blob/v3.3.7/launcher/src/main.rs#L769-L774",
        "se7504fa5bd0c": "https://github.com/huggingface/text-generation-inference/blob/v3.3.7/Dockerfile#L147-L149",
        "sbe4cfd078ceb": "https://github.com/huggingface/text-generation-inference/blob/v3.3.7/router/src/server.rs#L1906-L1910",
        "s3f8623221ee5": "https://github.com/huggingface/text-generation-inference/blob/v3.3.7/launcher/src/main.rs"
      }
    },
    "tgi-router": {
      "name": "TGI router",
      "basis": "24ee40d143d8d046039f12f76940a85886cbe152",
      "sources": {
        "sc46baeb2e20d": "https://github.com/huggingface/text-generation-inference/blob/24ee40d143d8d046039f12f76940a85886cbe152/router/src/server.rs"
      }
    },
    "tgi-docs": {
      "name": "TGI documentation",
      "basis": "unknown",
      "sources": {
        "s07efbedb395d": "https://github.com/huggingface/text-generation-inference",
        "sf21d69ac884f": "https://huggingface.co/docs/text-generation-inference/reference/launcher"
      }
    },
    "sglang": {
      "name": "SGLang",
      "basis": "v0.5.20",
      "sources": {
        "saf08ef6910b0": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/arg_groups/fields/serving.py#L72-L73",
        "sbf57dc2f54d2": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/arg_groups/fields/serving.py#L155-L162",
        "sa5df753aef88": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/utils/auth.py#L145-L151",
        "scce1a63feba8": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/server_args.py#L397-L399",
        "s0a4966847154": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/utils/server_args_config_parser.py#L118-L187",
        "scc4de2d1f4bc": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/environ.py",
        "s50e55d90147c": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/entrypoints/engine.py#L1109",
        "se29cdc6dade1": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/server_args.py#L311-L325",
        "sd5cd1ab725c3": "https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/entrypoints/http_server.py#L818-L850",
        "sd4ed6d838a92": "https://docs.sglang.io/docs/advanced_features/server_arguments"
      }
    },
    "triton": {
      "name": "Triton source",
      "basis": "546a78766fb112128aa0b10a70c55f4f39c3b1df",
      "sources": {
        "s33bf29bf71da": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.h#L191-L219",
        "s67ab19969241": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.h#L51-L67",
        "sf92f4669ae27": "https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/deploy.html",
        "sa915d43059a2": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L708-L725",
        "sc8b533580b3b": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L558-L576",
        "s5f927b497e5d": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L508-L516",
        "s705af5df3dd8": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L632-L640",
        "s1b9ce89125bd": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/restricted_features.h#L37-L112",
        "sa9c069223fba": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L2095-L2163",
        "s79fae2bcb514": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L3324-L3334",
        "s2a4cdfc6be30": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L4939-L4953",
        "s7f5038fa0fe2": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L2031-L2149",
        "s2fee6c80ec1d": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.h#L180-L188",
        "s4b469f1c21de": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L1759-L2027",
        "sce84579a9a6e": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/tracer.cc#L1244-L1249",
        "s682fdddf06a8": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/tracer.cc#L221-L232",
        "sc68b8b9a1b21": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L739-L750",
        "sb1f8ac2356f6": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_shared_memory.md#L29-L68",
        "s601665063934": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L2177-L2378",
        "s9fe885785c49": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_shared_memory.md#L65-L68",
        "s6f16e1d770dc": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_model_repository.md#L136-L152",
        "s48cab4cab77d": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_model_repository.md#L350-L400",
        "sa63a1d3d8242": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_model_repository.md#L59-L90",
        "s7d85aace8e33": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L424-L434",
        "s8501fbc9ecb4": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L1684-L1755",
        "s2f7f38a83db9": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.cc#L194-L225",
        "s614cd673f20f": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.h#L47-L49",
        "sad0e75f73ba4": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/sagemaker_server.cc#L198-L225",
        "s672bf7fa57b3": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/vertex_ai_server.cc#L142-L145",
        "s0c7905e1e132": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/vertex_ai_server.cc#L245-L272",
        "s0ce822aef316": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/vertex_ai_server.cc#L34-L37",
        "se9f3f1a88325": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L308-L345",
        "s9cd72f11c287": "https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.h#L143-L157"
      }
    },
    "lmstudio": {
      "name": "LM Studio documentation",
      "basis": "unknown",
      "sources": {
        "s776be8700529": "https://lmstudio.ai/docs/developer/core/server",
        "s6b9f80dc5c59": "https://lmstudio.ai/docs/developer/core/server/serve-on-network",
        "sb756d0785d3d": "https://lmstudio.ai/docs/developer/openai-compat",
        "sb940f6563319": "https://lmstudio.ai/docs/developer/core/authentication",
        "sb7e0fa7490b2": "https://lmstudio.ai/docs/developer/core/server/settings"
      }
    },
    "webui": {
      "name": "text-generation-webui source",
      "basis": "c022565b1257a9c7d9a5128c8b4c03587559cf08",
      "sources": {
        "sf47dbc117b02": "https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/shared.py",
        "sfafd8b6e5106": "https://github.com/oobabooga/text-generation-webui#command-line-flags",
        "sfbacbf383d45": "https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/server.py#L90-L95",
        "s304dbbc211b7": "https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/api/script.py#L594-L597",
        "s578896c6eca6": "https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/shared.py#L50",
        "s75153f5981cf": "https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/paths.py#L5-L21",
        "s4010efbd61e8": "https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/user_data/CMD_FLAGS.txt",
        "s77fccc0c7e77": "https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/one_click.py#L24"
      }
    },
    "webui-api": {
      "name": "text-generation-webui API source",
      "basis": "619a2b8ee4b7e48541a9be5c07e04cd31b91b44f",
      "sources": {
        "s6c159a552ded": "https://github.com/oobabooga/text-generation-webui/blob/619a2b8ee4b7e48541a9be5c07e04cd31b91b44f/modules/api/script.py",
        "sbafd006b7156": "https://github.com/oobabooga/text-generation-webui/blob/619a2b8ee4b7e48541a9be5c07e04cd31b91b44f/modules/api/script.py#L599-L602"
      }
    },
    "webui-docs": {
      "name": "text-generation-webui API documentation",
      "basis": "ceade2eb1ba3f84518076270df2240b6bbb01da0",
      "sources": {
        "sfc908ade10d1": "https://github.com/oobabooga/text-generation-webui/blob/ceade2eb1ba3f84518076270df2240b6bbb01da0/docs/12%20-%20OpenAI%20API.md"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "llama-bind": {"text": "llama-server defaults to 127.0.0.1:8080; retain loopback and exclude inherited LLAMA_ARG_* overrides.", "components": ["llama"], "sources": ["llama:s808f8d1c8da9"], "status": "REASONED"},
    "llama-key": {"text": "api-key-file reads one key per line, with # comments; protect the plaintext file and avoid argv/environment secret exposure.", "components": ["llama"], "sources": ["llama:s808f8d1c8da9"], "status": "REASONED"},
    "llama-env": {"text": "Clear LLAMA_API_KEY and LLAMA_ARG_API_KEY_FILE; reject a file without a key line and test native refusal/acceptance directly.", "components": ["llama"], "sources": ["llama:s808f8d1c8da9"], "status": "REASONED"},
    "llama-tls": {"text": "Native PEM TLS needs a build with DLLAMA_OPENSSL=ON and ssl-key-file/ssl-cert-file; otherwise use a TLS proxy.", "components": ["llama"], "sources": ["llama:s808f8d1c8da9"], "status": "REASONED"},
    "vllm-key": {"text": "At both source commits --api-key takes precedence over VLLM_API_KEY fallback; keep secrets out of launch argv.", "components": ["vllm-a", "vllm-b"], "sources": ["vllm-a:s7b472d8bd2d0", "vllm-b:sdbf0512be177", "vllm-a:sd13651484ed1", "vllm-b:se5d922e084ed"], "status": "REASONED"},
    "vllm-file": {"text": "Use protected YAML via two-word --config FILE; --config=FILE is accepted without loading the key; clear inherited VLLM_API_KEY.", "components": ["vllm-a"], "sources": ["vllm-a:safb9d5e38921", "vllm-a:sd13651484ed1"], "status": "REASONED"},
    "vllm-process": {"text": "Python spawn transfers API server arguments through a pipe; opt-in Rust frontend puts api_key in --args-json argv, so clear VLLM_USE_RUST_FRONTEND.", "components": ["vllm-a"], "sources": ["vllm-a:sccd45a9ffb02", "vllm-a:sc14e6c37774c", "vllm-a:sba4bc217b9de"], "status": "REASONED"},
    "vllm-logs": {"text": "HTTP startup redacts api_key, but gRPC logs the argument set unredacted; protect those logs.", "components": ["vllm-a"], "sources": ["vllm-a:scf43e725574b", "vllm-a:s4b161060c056"], "status": "REASONED"},
    "vllm-scope": {"text": "API key covers /v1, /v2, /inference and /cohere; /invocations, enabled profiler routes and unprotected plugins remain outside it.", "components": ["vllm"], "sources": ["vllm:s65a60be2808c", "vllm:s36fcb4c4fc18"], "status": "REASONED", "verify": [1]},
    "vllm-bind": {"text": "Unset frontend host listens on 0.0.0.0:8000; explicitly select 127.0.0.1.", "components": ["vllm"], "sources": ["vllm:s90b2ada8e38b", "vllm:sb9c63e342665", "vllm:s701a469f3c23"], "status": "REASONED"},
    "vllm-tls": {"text": "Frontend ssl-keyfile, ssl-certfile and ssl-ca-certs support TLS; proxy or tunnel remains the recommended boundary.", "components": ["vllm-a"], "sources": ["vllm-a:s7b472d8bd2d0"], "status": "REASONED"},
    "vllm-isolation": {"text": "HTTP key/TLS do not protect internal TCPStore, ZMQ or collective channels; isolate trusted cluster members and treat Ray as one trust domain.", "components": ["vllm"], "sources": ["vllm:se5660cf62498", "vllm:sec32bab94990", "vllm:s1de6a9f4ed49"], "status": "REASONED"},
    "vllm-store": {"text": "TCPStore can bind all interfaces; stateless rank-zero binding and other rendezvous paths differ; inventory actual transport sockets.", "components": ["vllm"], "sources": ["vllm:sd18839fe8984", "vllm:s27ba1937dca0", "vllm:s7abb84b61c6e", "vllm:se5660cf62498"], "status": "REASONED"},
    "vllm-master": {"text": "Multi-node multiprocessing uses master-addr and master-port, default 29501; DP adds ports and Ray V2 can bind port zero.", "components": ["vllm"], "sources": ["vllm:s1fc694d68aac", "vllm:s8c1221a0c7b9", "vllm:s15bf642ce14e"], "status": "REASONED"},
    "vllm-handshake": {"text": "Remote/elastic multiprocessing DP uses startup TCP handshake on data-parallel-address/rpc-port, default 29550; otherwise IPC, with Ray bypassing that constructor.", "components": ["vllm"], "sources": ["vllm:sfecabc3bc16d", "vllm:se3e528b9ca5c", "vllm:s1fc694d68aac"], "status": "REASONED"},
    "vllm-channels": {"text": "Remote engine request/result and coordinator channels use dynamic TCP, local paths generally IPC with elastic exceptions.", "components": ["vllm"], "sources": ["vllm:sfecabc3bc16d", "vllm:se3e528b9ca5c", "vllm:s8ddf90ed2cb1"], "status": "REASONED"},
    "vllm-queues": {"text": "Worker queues add dynamic TCP only for remote readers, using detected multiprocessing or Ray node addresses; headless removes only the HTTP frontend.", "components": ["vllm"], "sources": ["vllm:sb6a7effd4318", "vllm:s2dad806d290a", "vllm:s66d892167b5d", "vllm:s19f4f6a6790f"], "status": "REASONED"},
    "nixl": {"text": "Opt-in NIXL handshake defaults localhost:5600 plus DP index and starts with metadata; its host/port settings are separate.", "components": ["vllm"], "sources": ["vllm:sdb9dac146cd4", "vllm:s0ec5750d8161", "vllm:s2c10a0015812"], "status": "REASONED"},
    "mooncake": {"text": "Producer/kv_both bootstrap uses wildcard 8998 at selected ranks; producer workers use node IP/dynamic ports; consumer-only workers omit those listeners.", "components": ["vllm"], "sources": ["vllm:s97fe4257dfc6", "vllm:s623327f195f8", "vllm:s0341e26f43ae", "vllm:s0fa9693f3666"], "status": "REASONED"},
    "vllm-grpc": {"text": "Optional gRPC replaces HTTP with unauthenticated plaintext on host/port, default 0.0.0.0:8000; the documented grpc-port does not match this CLI.", "components": ["vllm"], "sources": ["vllm:sd52612723dde", "vllm:sb6766a13ce4a"], "status": "REASONED"},
    "vllm-supervisor": {"text": "Multi-port external-LB mode adds keyless health supervision after child readiness on host:9256 by default; frontend TLS options apply.", "components": ["vllm"], "sources": ["vllm:sbc83e9d09208", "vllm:s471a29420e3a", "vllm:s80888a79d6e2", "vllm:s7d70cef86248", "vllm:sd80aa5c7d7cc"], "status": "REASONED"},
    "vllm-node-ip": {"text": "Set per-node VLLM_HOST_IP and serving master/DP addresses deliberately; automatic node detection can choose public IP or fall back to wildcard.", "components": ["vllm"], "sources": ["vllm:sdf64db690b1c", "vllm:s0497a5e3fe44", "vllm:s92bab6d08b69"], "status": "REASONED"},
    "vllm-ports": {"text": "VLLM_PORT starts allocation, not a firewall range; DP fallback variables are not serving-flag substitutes and DP master port also reserves ten ports.", "components": ["vllm"], "sources": ["vllm:s7cb33671d83d", "vllm:scfeadcdcd9a1", "vllm:s92bab6d08b69"], "status": "REASONED"},
    "vllm-single": {"text": "Single-GPU normally uses file store/local IPC with ROCm AITER TCP exception; Gloo groups still require listener inventory.", "components": ["vllm"], "sources": ["vllm:s3b1ce10c3e66", "vllm:s67bc8be47a91", "vllm:sed65b4428b70"], "status": "REASONED"},
    "tgi-bind": {"text": "Launcher defaults 0.0.0.0:3000 via hostname/port flags or HOSTNAME/PORT; bind privately.", "components": ["tgi"], "sources": ["tgi:s6d442de48f37"], "status": "REASONED"},
    "tgi-image": {"text": "Main image sets PORT=80; Docker's non-IP hostname makes router fall back to wildcard.", "components": ["tgi"], "sources": ["tgi:se7504fa5bd0c", "tgi:sbe4cfd078ceb"], "status": "REASONED"},
    "tgi-lifecycle": {"text": "Guide records maintenance mode and archive on 2026-03-21; retain controls and plan migration.", "components": ["tgi-docs"], "sources": ["tgi-docs:s07efbedb395d"], "status": "REASONED"},
    "tgi-key-argv": {"text": "Launcher passes API_KEY or --api-key to router argv; no launcher input avoids that exposure to local process observers.", "components": ["tgi"], "sources": ["tgi:s3f8623221ee5"], "status": "REASONED"},
    "tgi-auth": {"text": "Bearer middleware protects base inference routes with 401, not health/info/metrics, KServe, v1/models or Vertex prediction; enforce proxy allowlists/auth.", "components": ["tgi-router"], "sources": ["tgi-router:sc46baeb2e20d"], "status": "REASONED"},
    "tgi-tls": {"text": "Launcher has no TLS option; terminate TLS in front.", "components": ["tgi-docs"], "sources": ["tgi-docs:sf21d69ac884f"], "status": "REASONED"},
    "tgi-metrics": {"text": "Separate Prometheus listener defaults 9000 and is unauthenticated; keep it private.", "components": ["tgi-docs", "tgi"], "sources": ["tgi-docs:sf21d69ac884f", "tgi:s3f8623221ee5"], "status": "REASONED"},
    "sglang-bind": {"text": "SGLang defaults 127.0.0.1:30000; retain private host/port.", "components": ["sglang"], "sources": ["sglang:saf08ef6910b0"], "status": "REASONED"},
    "sglang-auth": {"text": "api-key protects ordinary endpoints; admin-api-key separately protects administrative operations, not server_info; an empty API key leaves ordinary requests open.", "components": ["sglang"], "sources": ["sglang:sbf57dc2f54d2", "sglang:sa5df753aef88"], "status": "REASONED"},
    "sglang-file": {"text": "Protected YAML --config keeps both keys out of kernel argv; no documented stdin/environment input exists at the pin.", "components": ["sglang"], "sources": ["sglang:scce1a63feba8", "sglang:s0a4966847154", "sglang:scc4de2d1f4bc"], "status": "REASONED"},
    "sglang-log": {"text": "INFO startup logs all resolved server_args including both keys; protect the log.", "components": ["sglang"], "sources": ["sglang:s50e55d90147c", "sglang:se29cdc6dade1"], "status": "REASONED"},
    "sglang-info": {"text": "server_info/get_server_info expose resolved keys and launch_command to ordinary API-key holders; exclude them or trust those holders with admin authority.", "components": ["sglang"], "sources": ["sglang:sd5cd1ab725c3", "sglang:se29cdc6dade1", "sglang:sa5df753aef88"], "status": "REASONED"},
    "sglang-tls": {"text": "ssl-keyfile/ssl-certfile/ssl-ca-certs provide native TLS; enable-ssl-refresh reloads renewed certificates.", "components": ["sglang"], "sources": ["sglang:sd4ed6d838a92"], "status": "REASONED"},
    "triton-listeners": {"text": "Triton defaults to wildcard HTTP 8000, gRPC 8001 and metrics 8002; bind each privately.", "components": ["triton"], "sources": ["triton:s33bf29bf71da", "triton:s67ab19969241"], "status": "REASONED"},
    "triton-protocols": {"text": "HTTP/gRPC default enabled; disable unused protocols and metrics, while keeping gateway authorization.", "components": ["triton"], "sources": ["triton:sf92f4669ae27", "triton:s33bf29bf71da", "triton:sa915d43059a2"], "status": "REASONED"},
    "triton-tls": {"text": "gRPC supports TLS and mutual TLS with certificate/key flags; HTTP requires fronting TLS.", "components": ["triton"], "sources": ["triton:sc8b533580b3b", "triton:s67ab19969241"], "status": "REASONED"},
    "triton-secrets": {"text": "Restricted-API secrets are argv-only, visible for process lifetime and possibly retained by audit/orchestrator records; they do not protect against local readers.", "components": ["triton"], "sources": ["triton:s5f927b497e5d", "triton:s705af5df3dd8"], "status": "REASONED"},
    "triton-categories": {"text": "All nine compiled categories default unrestricted; restrictions are per category/protocol, and groups must not overlap.", "components": ["triton"], "sources": ["triton:s1b9ce89125bd", "triton:sa9c069223fba"], "status": "REASONED"},
    "triton-health": {"text": "Unrestricted health/metadata/inference, including HTTP generate/generate_stream, need no key; restricting health also affects probes.", "components": ["triton"], "sources": ["triton:s1b9ce89125bd", "triton:s79fae2bcb514", "triton:s2a4cdfc6be30"], "status": "REASONED"},
    "triton-logging": {"text": "Logging API reads settings/file path and changes verbosity/format/levels, but cannot change log_file.", "components": ["triton"], "sources": ["triton:s7f5038fa0fe2"], "status": "REASONED"},
    "triton-trace": {"text": "Trace settings API remains available when tracing is OFF; default triton mode needs a startup file path before enabling tracing, and API cannot change that path.", "components": ["triton"], "sources": ["triton:s2fee6c80ec1d", "triton:s4b469f1c21de", "triton:sce84579a9a6e", "triton:s682fdddf06a8", "triton:sc68b8b9a1b21"], "status": "REASONED"},
    "triton-shm": {"text": "Shared-memory status is readable; registration/use defaults off until allow-client-shm=true, with GPU/platform restrictions.", "components": ["triton"], "sources": ["triton:sb1f8ac2356f6", "triton:s601665063934", "triton:s9fe885785c49"], "status": "REASONED"},
    "triton-repository": {"text": "Repository index is readable; API load/unload require explicit mode, not default none or poll, and can accept config/inline files or unload dependents.", "components": ["triton"], "sources": ["triton:s6f16e1d770dc", "triton:s48cab4cab77d", "triton:sa63a1d3d8242", "triton:s7d85aace8e33"], "status": "REASONED"},
    "triton-reads": {"text": "Model-config and supported statistics reads are independent of model-control mode.", "components": ["triton"], "sources": ["triton:s8501fbc9ecb4"], "status": "REASONED"},
    "triton-denial": {"text": "HTTP expects configured header and returns 403 on failure; gRPC prefixes triton-grpc-protocol- and returns UNAVAILABLE with restriction message.", "components": ["triton"], "sources": ["triton:sa9c069223fba", "triton:s2f7f38a83db9", "triton:s614cd673f20f", "triton:s2a4cdfc6be30"], "status": "REASONED"},
    "triton-cloud": {"text": "Conditional Vertex/SageMaker listeners need separate inventory/isolation; SageMaker invoke bypasses restrictions and Vertex redirect headers can reach unrestricted metrics.", "components": ["triton"], "sources": ["triton:sad0e75f73ba4", "triton:s672bf7fa57b3", "triton:s0c7905e1e132", "triton:s0ce822aef316"], "status": "REASONED"},
    "triton-metrics": {"text": "Metrics 8002 at /metrics or /metrics/ is unauthenticated and outside both restriction flags; isolate or disable it.", "components": ["triton"], "sources": ["triton:sa915d43059a2", "triton:se9f3f1a88325", "triton:s9cd72f11c287"], "status": "REASONED"},
    "lmstudio-bind": {"text": "Desktop server uses localhost:1234; Serve on Local Network or bind 0.0.0.0 widens access.", "components": ["lmstudio"], "sources": ["lmstudio:s776be8700529", "lmstudio:s6b9f80dc5c59", "lmstudio:sb756d0785d3d"], "status": "REASONED"},
    "lmstudio-auth": {"text": "Authentication defaults off; Require Authentication and bearer tokens are documented for 0.4.0+; enable before remote access.", "components": ["lmstudio"], "sources": ["lmstudio:sb940f6563319"], "status": "REASONED"},
    "lmstudio-tls": {"text": "Server settings list no TLS; use a tailnet or authenticated TLS proxy for remote access.", "components": ["lmstudio"], "sources": ["lmstudio:sb7e0fa7490b2"], "status": "REASONED"},
    "webui-listeners": {"text": "Gradio defaults 127.0.0.1:7860; optional --api defaults 127.0.0.1:5000; both start unauthenticated.", "components": ["webui", "webui-api"], "sources": ["webui:sf47dbc117b02", "webui-api:s6c159a552ded"], "status": "REASONED"},
    "webui-bind": {"text": "--listen widens both enabled surfaces; listen-port/api-port move them and listen-host only works with listen.", "components": ["webui", "webui-api"], "sources": ["webui:sf47dbc117b02", "webui-api:s6c159a552ded"], "status": "REASONED"},
    "webui-publication": {"text": "--share publishes Gradio UI and --public-api publishes API through a Cloudflare tunnel; treat both as publication.", "components": ["webui", "webui-api"], "sources": ["webui:sfafd8b6e5106", "webui-api:s6c159a552ded"], "status": "REASONED"},
    "webui-ui-auth": {"text": "gradio-auth-path protects UI only; file entries split on commas/newlines and every colon, so use permitted username and generated hex password.", "components": ["webui"], "sources": ["webui:sfbacbf383d45"], "status": "REASONED"},
    "webui-api-auth": {"text": "api-key protects OpenAI routes via bearer and Anthropic messages via x-api-key; admin-key protects administration and defaults to api-key, not vice versa.", "components": ["webui-api", "webui-docs"], "sources": ["webui-api:s6c159a552ded", "webui-docs:sfc908ade10d1"], "status": "REASONED"},
    "webui-key-logs": {"text": "API startup logs api-key and distinct admin-key in plaintext at INFO; protect output and rotate after disclosure.", "components": ["webui-api", "webui"], "sources": ["webui-api:sbafd006b7156", "webui:s304dbbc211b7"], "status": "REASONED"},
    "webui-file": {"text": "API keys lack file/environment flags; private external user-data-dir CMD_FLAGS.txt supplies in-process arguments, keeping keys out of kernel argv.", "components": ["webui"], "sources": ["webui:sf47dbc117b02", "webui:s578896c6eca6", "webui:s75153f5981cf"], "status": "REASONED"},
    "webui-checkout": {"text": "Checkout CMD_FLAGS.txt is tracked; git diff/stash and one-click autostash/reset can expose or discard keys; use a new private directory outside checkout.", "components": ["webui"], "sources": ["webui:s4010efbd61e8", "webui:s77fccc0c7e77"], "status": "REASONED"},
    "webui-launcher": {"text": "Run server.py directly: one-click unquoted argument joining and shell=True can split paths or execute shell syntax.", "components": ["webui"], "sources": ["webui:s77fccc0c7e77"], "status": "REASONED"},
    "webui-api-only": {"text": "--api --nowebui removes UI; ssl-keyfile/ssl-certfile provide both surfaces TLS, with proxy TLS/auth the recommended pattern.", "components": ["webui", "webui-docs"], "sources": ["webui:sf47dbc117b02", "webui-docs:sfc908ade10d1"], "status": "REASONED"},
    "webui-host": {"text": "Loopback API rejects Host other than localhost/127.0.0.1 with 400 unless listen/public-api is set; proxy must rewrite Host.", "components": ["webui-api"], "sources": ["webui-api:s6c159a552ded"], "status": "REASONED"},
    "verify-listeners": {"text": "Inspect all backend listeners, namespaces and publications; ss alone proves no external isolation.", "components": ["llama", "vllm", "tgi", "triton", "sglang"], "sources": ["llama:s808f8d1c8da9", "vllm:s90b2ada8e38b", "tgi:s6d442de48f37", "triton:s33bf29bf71da", "sglang:saf08ef6910b0"], "status": "REASONED", "verify": [1]},
    "verify-proxy-auth": {"text": "Proxy model-list probes expect no-key 401 and keyed 200/list; TGI model listing does not establish native key enforcement.", "components": ["tgi-router", "curl"], "sources": ["tgi-router:sc46baeb2e20d", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-invocations": {"text": "Use valid JSON/served model and upstream evidence: unknown-model 404 or proxy-intercepted errors cannot establish vLLM route denial.", "components": ["vllm"], "sources": ["vllm:s65a60be2808c", "vllm:s36fcb4c4fc18"], "status": "REASONED", "verify": [1]},
    "verify-webui": {"text": "No-key API model-list 200 is exposure, 401 auth; TLS/transport errors or invalid Host are inconclusive and proxy rejection proves only proxy policy.", "components": ["webui-api", "curl"], "sources": ["webui-api:s6c159a552ded", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [2]},
    "verify-triton": {"text": "Direct HTTP logging should change from 200/settings to 403/restriction; other errors prove neither this control nor other categories/protocols.", "components": ["triton", "curl"], "sources": ["triton:s7f5038fa0fe2", "triton:s2a4cdfc6be30", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [3]},
    "verify-cluster": {"text": "Inventory startup/dynamic sockets; trusted peers connect to cross-node endpoints while outsiders fail with firewall evidence; local-only endpoints need local positive controls.", "components": ["vllm"], "sources": ["vllm:se5660cf62498", "vllm:sfecabc3bc16d", "vllm:se3e528b9ca5c"], "status": "REASONED", "verify": [4]},
    "verify-transport": {"text": "TCP probe establishes only reachability; stale ports, wrong address or stopped service are inconclusive, and RDMA/non-TCP need separate tests.", "components": ["vllm"], "sources": ["vllm:se5660cf62498", "vllm:sec32bab94990"], "status": "REASONED", "verify": [4]},
    "vllm-parser-run": {"text": "Isolated parser harness with stubbed logger/minimal serve parser loaded --config FILE but not --config=FILE; no vLLM server was run.", "components": ["vllm-a"], "sources": ["vllm-a:safb9d5e38921"], "status": "DEMONSTRATED", "evidence": "The pinned parser class was also run on its own, outside vLLM, with vLLM's logger stubbed and a minimal `serve` parser in place of vLLM's own: with `--config FILE` it turned the generated file's `api-key` line into a one-element key list, and with `--config=FILE` it left the key unset."},
    "webui-parser-run": {"text": "Imported shared.py parsed keys and a later flag from a private path containing a space while kernel cmdline held neither; no server was run.", "components": ["webui"], "sources": ["webui:s578896c6eca6"], "status": "DEMONSTRATED", "evidence": "The pinned `modules/shared.py`, imported with `--user-data-dir` pointing at a directory the block had written (a path containing a space, with a `--listen-port` line added after the key lines), parsed both keys and that flag from `CMD_FLAGS.txt` while the process's `/proc/self/cmdline` held neither"},
    "argv-test": {"text": "Recorded procps-ng 4.0.4 stub-process checks distinguish named secret flags from file flags; JSON, abbreviations, hidden/scrubbed argv remain misses.", "components": ["llama", "vllm-a", "sglang", "tgi", "webui", "triton"], "sources": ["llama:s808f8d1c8da9", "vllm-a:s7b472d8bd2d0", "sglang:sbf57dc2f54d2", "tgi:s3f8623221ee5", "webui:sf47dbc117b02", "triton:s5f927b497e5d"], "status": "DEMONSTRATED", "evidence": "`--api-key DUMMY_NOT_A_SECRET`, `--admin-key DUMMY_NOT_A_SECRET`, `--admin-api-key=DUMMY_NOT_A_SECRET`, `--gradio-auth u:DUMMY_NOT_A_SECRET`, `--http-restricted-api=model-repository:admin-key=DUMMY_NOT_A_SECRET`, `--grpc-restricted-protocol=model-repository:admin-key=DUMMY_NOT_A_SECRET` and an empty `--api-key=` each counted `1`"}
  }
}
---
# Model servers: llama.cpp, vLLM, TGI, SGLang, Triton, and LM Studio

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| llama-bind: llama-server defaults to 127.0.0.1:8080; retain loopback and exclude inherited LLAMA_ARG_* overrides. | llama.cpp e0dff58475bc9ed68eedcb265ee998f2fcabb3b1 | REASONED |
| llama-key: api-key-file reads one key per line, with # comments; protect the plaintext file and avoid argv/environment secret exposure. | llama.cpp e0dff58475bc9ed68eedcb265ee998f2fcabb3b1 | REASONED |
| llama-env: Clear LLAMA_API_KEY and LLAMA_ARG_API_KEY_FILE; reject a file without a key line and test native refusal/acceptance directly. | llama.cpp e0dff58475bc9ed68eedcb265ee998f2fcabb3b1 | REASONED |
| llama-tls: Native PEM TLS needs a build with DLLAMA_OPENSSL=ON and ssl-key-file/ssl-cert-file; otherwise use a TLS proxy. | llama.cpp e0dff58475bc9ed68eedcb265ee998f2fcabb3b1 | REASONED |
| vllm-key: At both source commits --api-key takes precedence over VLLM_API_KEY fallback; keep secrets out of launch argv. | vLLM source dee37d89115db4c94a820a79a78a7828e141c910; vLLM second source 8c1557a79c539ffe82d004d2a0c8d7b5e71159ce | REASONED |
| vllm-file: Use protected YAML via two-word --config FILE; --config=FILE is accepted without loading the key; clear inherited VLLM_API_KEY. | vLLM source dee37d89115db4c94a820a79a78a7828e141c910 | REASONED |
| vllm-process: Python spawn transfers API server arguments through a pipe; opt-in Rust frontend puts api_key in --args-json argv, so clear VLLM_USE_RUST_FRONTEND. | vLLM source dee37d89115db4c94a820a79a78a7828e141c910 | REASONED |
| vllm-logs: HTTP startup redacts api_key, but gRPC logs the argument set unredacted; protect those logs. | vLLM source dee37d89115db4c94a820a79a78a7828e141c910 | REASONED |
| vllm-scope: API key covers /v1, /v2, /inference and /cohere; /invocations, enabled profiler routes and unprotected plugins remain outside it. | vLLM v0.30.0 | REASONED |
| vllm-bind: Unset frontend host listens on 0.0.0.0:8000; explicitly select 127.0.0.1. | vLLM v0.30.0 | REASONED |
| vllm-tls: Frontend ssl-keyfile, ssl-certfile and ssl-ca-certs support TLS; proxy or tunnel remains the recommended boundary. | vLLM source dee37d89115db4c94a820a79a78a7828e141c910 | REASONED |
| vllm-isolation: HTTP key/TLS do not protect internal TCPStore, ZMQ or collective channels; isolate trusted cluster members and treat Ray as one trust domain. | vLLM v0.30.0 | REASONED |
| vllm-store: TCPStore can bind all interfaces; stateless rank-zero binding and other rendezvous paths differ; inventory actual transport sockets. | vLLM v0.30.0 | REASONED |
| vllm-master: Multi-node multiprocessing uses master-addr and master-port, default 29501; DP adds ports and Ray V2 can bind port zero. | vLLM v0.30.0 | REASONED |
| vllm-handshake: Remote/elastic multiprocessing DP uses startup TCP handshake on data-parallel-address/rpc-port, default 29550; otherwise IPC, with Ray bypassing that constructor. | vLLM v0.30.0 | REASONED |
| vllm-channels: Remote engine request/result and coordinator channels use dynamic TCP, local paths generally IPC with elastic exceptions. | vLLM v0.30.0 | REASONED |
| vllm-queues: Worker queues add dynamic TCP only for remote readers, using detected multiprocessing or Ray node addresses; headless removes only the HTTP frontend. | vLLM v0.30.0 | REASONED |
| nixl: Opt-in NIXL handshake defaults localhost:5600 plus DP index and starts with metadata; its host/port settings are separate. | vLLM v0.30.0 | REASONED |
| mooncake: Producer/kv_both bootstrap uses wildcard 8998 at selected ranks; producer workers use node IP/dynamic ports; consumer-only workers omit those listeners. | vLLM v0.30.0 | REASONED |
| vllm-grpc: Optional gRPC replaces HTTP with unauthenticated plaintext on host/port, default 0.0.0.0:8000; the documented grpc-port does not match this CLI. | vLLM v0.30.0 | REASONED |
| vllm-supervisor: Multi-port external-LB mode adds keyless health supervision after child readiness on host:9256 by default; frontend TLS options apply. | vLLM v0.30.0 | REASONED |
| vllm-node-ip: Set per-node VLLM_HOST_IP and serving master/DP addresses deliberately; automatic node detection can choose public IP or fall back to wildcard. | vLLM v0.30.0 | REASONED |
| vllm-ports: VLLM_PORT starts allocation, not a firewall range; DP fallback variables are not serving-flag substitutes and DP master port also reserves ten ports. | vLLM v0.30.0 | REASONED |
| vllm-single: Single-GPU normally uses file store/local IPC with ROCm AITER TCP exception; Gloo groups still require listener inventory. | vLLM v0.30.0 | REASONED |
| tgi-bind: Launcher defaults 0.0.0.0:3000 via hostname/port flags or HOSTNAME/PORT; bind privately. | TGI launcher/image v3.3.7 | REASONED |
| tgi-image: Main image sets PORT=80; Docker's non-IP hostname makes router fall back to wildcard. | TGI launcher/image v3.3.7 | REASONED |
| tgi-lifecycle: Guide records maintenance mode and archive on 2026-03-21; retain controls and plan migration. | TGI documentation unknown | REASONED |
| tgi-key-argv: Launcher passes API_KEY or --api-key to router argv; no launcher input avoids that exposure to local process observers. | TGI launcher/image v3.3.7 | REASONED |
| tgi-auth: Bearer middleware protects base inference routes with 401, not health/info/metrics, KServe, v1/models or Vertex prediction; enforce proxy allowlists/auth. | TGI router 24ee40d143d8d046039f12f76940a85886cbe152 | REASONED |
| tgi-tls: Launcher has no TLS option; terminate TLS in front. | TGI documentation unknown | REASONED |
| tgi-metrics: Separate Prometheus listener defaults 9000 and is unauthenticated; keep it private. | TGI documentation unknown; TGI launcher/image v3.3.7 | REASONED |
| sglang-bind: SGLang defaults 127.0.0.1:30000; retain private host/port. | SGLang v0.5.20 | REASONED |
| sglang-auth: api-key protects ordinary endpoints; admin-api-key separately protects administrative operations, not server_info; an empty API key leaves ordinary requests open. | SGLang v0.5.20 | REASONED |
| sglang-file: Protected YAML --config keeps both keys out of kernel argv; no documented stdin/environment input exists at the pin. | SGLang v0.5.20 | REASONED |
| sglang-log: INFO startup logs all resolved server_args including both keys; protect the log. | SGLang v0.5.20 | REASONED |
| sglang-info: server_info/get_server_info expose resolved keys and launch_command to ordinary API-key holders; exclude them or trust those holders with admin authority. | SGLang v0.5.20 | REASONED |
| sglang-tls: ssl-keyfile/ssl-certfile/ssl-ca-certs provide native TLS; enable-ssl-refresh reloads renewed certificates. | SGLang v0.5.20 | REASONED |
| triton-listeners: Triton defaults to wildcard HTTP 8000, gRPC 8001 and metrics 8002; bind each privately. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-protocols: HTTP/gRPC default enabled; disable unused protocols and metrics, while keeping gateway authorization. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-tls: gRPC supports TLS and mutual TLS with certificate/key flags; HTTP requires fronting TLS. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-secrets: Restricted-API secrets are argv-only, visible for process lifetime and possibly retained by audit/orchestrator records; they do not protect against local readers. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-categories: All nine compiled categories default unrestricted; restrictions are per category/protocol, and groups must not overlap. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-health: Unrestricted health/metadata/inference, including HTTP generate/generate_stream, need no key; restricting health also affects probes. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-logging: Logging API reads settings/file path and changes verbosity/format/levels, but cannot change log_file. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-trace: Trace settings API remains available when tracing is OFF; default triton mode needs a startup file path before enabling tracing, and API cannot change that path. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-shm: Shared-memory status is readable; registration/use defaults off until allow-client-shm=true, with GPU/platform restrictions. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-repository: Repository index is readable; API load/unload require explicit mode, not default none or poll, and can accept config/inline files or unload dependents. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-reads: Model-config and supported statistics reads are independent of model-control mode. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-denial: HTTP expects configured header and returns 403 on failure; gRPC prefixes triton-grpc-protocol- and returns UNAVAILABLE with restriction message. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-cloud: Conditional Vertex/SageMaker listeners need separate inventory/isolation; SageMaker invoke bypasses restrictions and Vertex redirect headers can reach unrestricted metrics. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| triton-metrics: Metrics 8002 at /metrics or /metrics/ is unauthenticated and outside both restriction flags; isolate or disable it. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | REASONED |
| lmstudio-bind: Desktop server uses localhost:1234; Serve on Local Network or bind 0.0.0.0 widens access. | LM Studio documentation unknown | REASONED |
| lmstudio-auth: Authentication defaults off; Require Authentication and bearer tokens are documented for 0.4.0+; enable before remote access. | LM Studio documentation unknown | REASONED |
| lmstudio-tls: Server settings list no TLS; use a tailnet or authenticated TLS proxy for remote access. | LM Studio documentation unknown | REASONED |
| webui-listeners: Gradio defaults 127.0.0.1:7860; optional --api defaults 127.0.0.1:5000; both start unauthenticated. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08; text-generation-webui API source 619a2b8ee4b7e48541a9be5c07e04cd31b91b44f | REASONED |
| webui-bind: --listen widens both enabled surfaces; listen-port/api-port move them and listen-host only works with listen. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08; text-generation-webui API source 619a2b8ee4b7e48541a9be5c07e04cd31b91b44f | REASONED |
| webui-publication: --share publishes Gradio UI and --public-api publishes API through a Cloudflare tunnel; treat both as publication. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08; text-generation-webui API source 619a2b8ee4b7e48541a9be5c07e04cd31b91b44f | REASONED |
| webui-ui-auth: gradio-auth-path protects UI only; file entries split on commas/newlines and every colon, so use permitted username and generated hex password. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08 | REASONED |
| webui-api-auth: api-key protects OpenAI routes via bearer and Anthropic messages via x-api-key; admin-key protects administration and defaults to api-key, not vice versa. | text-generation-webui API source 619a2b8ee4b7e48541a9be5c07e04cd31b91b44f; text-generation-webui API documentation ceade2eb1ba3f84518076270df2240b6bbb01da0 | REASONED |
| webui-key-logs: API startup logs api-key and distinct admin-key in plaintext at INFO; protect output and rotate after disclosure. | text-generation-webui API source 619a2b8ee4b7e48541a9be5c07e04cd31b91b44f; text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08 | REASONED |
| webui-file: API keys lack file/environment flags; private external user-data-dir CMD_FLAGS.txt supplies in-process arguments, keeping keys out of kernel argv. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08 | REASONED |
| webui-checkout: Checkout CMD_FLAGS.txt is tracked; git diff/stash and one-click autostash/reset can expose or discard keys; use a new private directory outside checkout. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08 | REASONED |
| webui-launcher: Run server.py directly: one-click unquoted argument joining and shell=True can split paths or execute shell syntax. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08 | REASONED |
| webui-api-only: --api --nowebui removes UI; ssl-keyfile/ssl-certfile provide both surfaces TLS, with proxy TLS/auth the recommended pattern. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08; text-generation-webui API documentation ceade2eb1ba3f84518076270df2240b6bbb01da0 | REASONED |
| webui-host: Loopback API rejects Host other than localhost/127.0.0.1 with 400 unless listen/public-api is set; proxy must rewrite Host. | text-generation-webui API source 619a2b8ee4b7e48541a9be5c07e04cd31b91b44f | REASONED |
| verify-listeners: Inspect all backend listeners, namespaces and publications; ss alone proves no external isolation. | llama.cpp e0dff58475bc9ed68eedcb265ee998f2fcabb3b1; vLLM v0.30.0; TGI launcher/image v3.3.7; Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df; SGLang v0.5.20 | REASONED |
| verify-proxy-auth: Proxy model-list probes expect no-key 401 and keyed 200/list; TGI model listing does not establish native key enforcement. | TGI router 24ee40d143d8d046039f12f76940a85886cbe152; curl minimum write-out version 7.75.0 | REASONED |
| verify-invocations: Use valid JSON/served model and upstream evidence: unknown-model 404 or proxy-intercepted errors cannot establish vLLM route denial. | vLLM v0.30.0 | REASONED |
| verify-webui: No-key API model-list 200 is exposure, 401 auth; TLS/transport errors or invalid Host are inconclusive and proxy rejection proves only proxy policy. | text-generation-webui API source 619a2b8ee4b7e48541a9be5c07e04cd31b91b44f; curl minimum write-out version 7.75.0 | REASONED |
| verify-triton: Direct HTTP logging should change from 200/settings to 403/restriction; other errors prove neither this control nor other categories/protocols. | Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df; curl minimum write-out version 7.75.0 | REASONED |
| verify-cluster: Inventory startup/dynamic sockets; trusted peers connect to cross-node endpoints while outsiders fail with firewall evidence; local-only endpoints need local positive controls. | vLLM v0.30.0 | REASONED |
| verify-transport: TCP probe establishes only reachability; stale ports, wrong address or stopped service are inconclusive, and RDMA/non-TCP need separate tests. | vLLM v0.30.0 | REASONED |
| vllm-parser-run: Isolated parser harness with stubbed logger/minimal serve parser loaded --config FILE but not --config=FILE; no vLLM server was run. | vLLM source dee37d89115db4c94a820a79a78a7828e141c910 | DEMONSTRATED |
| webui-parser-run: Imported shared.py parsed keys and a later flag from a private path containing a space while kernel cmdline held neither; no server was run. | text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08 | DEMONSTRATED |
| argv-test: Recorded procps-ng 4.0.4 stub-process checks distinguish named secret flags from file flags; JSON, abbreviations, hidden/scrubbed argv remain misses. | llama.cpp e0dff58475bc9ed68eedcb265ee998f2fcabb3b1; vLLM source dee37d89115db4c94a820a79a78a7828e141c910; SGLang v0.5.20; TGI launcher/image v3.3.7; text-generation-webui source c022565b1257a9c7d9a5128c8b4c03587559cf08; Triton source 546a78766fb112128aa0b10a70c55f4f39c3b1df | DEMONSTRATED |
<!-- version-basis:end -->

Self-hosted model servers follow the [ollama.md](ollama.md) pattern: exposing one means someone else's prompts run on your GPU. Most default to local use, but vLLM, TGI, and Triton bind to `0.0.0.0` out of the box, and Triton enables no authentication by default (its native controls, gRPC mutual TLS and shared-secret restricted APIs, do not replace the gateway). Keep every server on loopback or a private network, require an API key where the server supports one, and terminate TLS in front. LocalAI is an OpenAI-compatible model server too, but its bind and authentication controls are documented in [ai-infra-services.md](ai-infra-services.md) rather than here, so the facts live in one place.

## llama.cpp (llama-server)

`llama-server` listens on `127.0.0.1:8080` by default; keep that bind. Require a key, and hand it to the server in a file rather than on the command line: a key expanded into `--api-key` sits in argv, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the server's whole lifetime, and quoting does not change that. At the pinned llama.cpp commit, `--api-key-file` reads the keys from a file, one per line, and the pinned README documents no stdin input for them. Create the file once, as the account that runs `llama-server`:

```bash
(
  set -eC
  umask 077
  mkdir -p -- "$HOME/.config/llama-server"
  chmod 700 -- "$HOME/.config/llama-server"
  if [ -e "$HOME/.config/llama-server/api-keys" ] || [ -L "$HOME/.config/llama-server/api-keys" ]; then
    echo 'api-keys already exists in ~/.config/llama-server; nothing written'; exit 2
  fi
  openssl rand -hex 32 > "$HOME/.config/llama-server/api-keys"
)
```

`umask 077` applies before anything is written, so the directory is created mode `0700` and the file mode `0600`. The block makes the directory mode `0700` first and then refuses when `api-keys` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not), so running the block again cannot replace a key your clients already hold; `set -C` also refuses an existing regular file, and the explicit check handles the other forms. As with the other writers in this guide, these checks hold only in owner-only directories no other account can replace. If `openssl` fails, the block leaves an empty file behind: delete it before running the block again, and the launch block below refuses to start on it. The key goes from `openssl` straight into the file, so it never passes through a shell variable or a command line. Add one line per further client key; at the pinned commit a line that begins with `#` is a comment. Clients running as that account on this host can read the same file; give remote clients their copy through your secret store ([secrets.md](secrets.md)). The file holds the key in plaintext at rest, readable by that account, by root, and by any backup that copies it, so keep it and its backups out of source control.

Start the server from the file:

```bash
(
  { unset -n LLAMA_API_KEY LLAMA_ARG_API_KEY_FILE && unset -v LLAMA_API_KEY LLAMA_ARG_API_KEY_FILE; } 2>/dev/null ||
    { echo 'cannot clear LLAMA_API_KEY or LLAMA_ARG_API_KEY_FILE in this shell; not starting'; exit 2; }
  set -- "${!LLAMA_ARG_@}"
  [ "$#" -eq 0 ] || { printf 'LLAMA_ARG_* variables set in this shell:'; printf ' %s' "$@"; printf '; unset them first; not starting\n'; exit 2; }
  grep -q '^[^#[:space:]]' "$HOME/.config/llama-server/api-keys" ||
    { echo 'no key line in ~/.config/llama-server/api-keys; not starting'; exit 2; }
  llama-server -m model.gguf --api-key-file "$HOME/.config/llama-server/api-keys"
)
```

The pinned README also lists `LLAMA_API_KEY` as an environment input for `--api-key` and `LLAMA_ARG_API_KEY_FILE` for `--api-key-file`. The block clears both names first and refuses to start when it cannot (a readonly name in your shell), so an inherited value can neither become a key nor point the server at a different file. It then refuses to start while any other `LLAMA_ARG_*` variable is set in the calling shell, naming each: the pinned README gives most llama-server options an `LLAMA_ARG_*` environment input, `LLAMA_ARG_HOST` for `--host` among them, so an inherited one would start the server differently from what the block shows, on another interface included. Unset them, or start from a clean shell. A key passed through `LLAMA_API_KEY` would stay out of argv but remain readable through `/proc/<pid>/environ` by the same account and by root for the server's whole lifetime; the file avoids that channel.

The block refuses a file with no line that starts with a key character, so a file of blank lines and `#` comments alone is refused, but it cannot tell a real key from other text, and what llama-server does with a file that holds no key line was not checked at the pinned commit. Confirm the key is enforced by probing the llama.cpp backend DIRECTLY on its own host and port from the trusted network (not through the proxy, which returns its own 401/200 regardless): a no-key request must be refused there and a keyed request accepted.

Native TLS exists when the binary is built with OpenSSL (`-DLLAMA_OPENSSL=ON`): `--ssl-key-file` and `--ssl-cert-file` take PEM files ([self-signed.md](self-signed.md) or [free-certificates.md](free-certificates.md)). A reverse proxy per [nginx.md](nginx.md)/[caddy.md](caddy.md) is the alternative when your build lacks SSL support.

## vLLM (OpenAI-compatible server)

vLLM's server requires an API key when one is set: at both pinned commits `--api-key` sets it, and when that flag is unset the server falls back to the `VLLM_API_KEY` environment variable. Flags move between vLLM releases, so confirm `--api-key` and `--config` in `vllm serve --help` on your installed version. Do not put the key on the command line, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the server's whole lifetime. At the pinned commits `--config` reads the server options from a YAML file inside the process, so put the key in a file only the account running vLLM can read. Create it once, as that account:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -eC
  umask 077
  mkdir -p -- "$HOME/.config/vllm"
  chmod 700 -- "$HOME/.config/vllm"
  if [ -e "$HOME/.config/vllm/server.yaml" ] || [ -L "$HOME/.config/vllm/server.yaml" ]; then
    echo 'server.yaml already exists in ~/.config/vllm; nothing written'; exit 2
  fi
  set -- "$(openssl rand -hex 32)"
  [ "${#1}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  case "$1" in *[!0123456789abcdef]*) echo 'key generation failed; nothing written'; exit 2 ;; esac
  printf 'api-key: "%s"\n' "$1" > "$HOME/.config/vllm/server.yaml"
)
```

The block makes the directory mode `0700` first, then refuses, before it generates a key, when `server.yaml` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not), so a rerun cannot replace a key your clients already hold. It writes nothing unless the generated key is 64 hex characters. `umask 077` creates the directory mode `0700` and the file mode `0600`, and `set -C` still refuses to overwrite an existing regular file. These checks run before the write, not atomically with it, so they hold only while no other account can replace the directory or any directory above it: run the block in owner-only directories you control, such as your own home directory, never under a path another account can write to. The key passes only through the subshell's positional parameters and the builtin `printf`, never a command line; the block clears inherited traps first because a DEBUG, RETURN or ERR trap from your shell could otherwise read it, and it assumes a clean shell. Start the server with only non-secret values on its command line, substituting your model inside the quotes, and do not add `--api-key` there, which would put the value back in argv:

```bash
(
  { unset -n VLLM_API_KEY VLLM_USE_RUST_FRONTEND && unset -v VLLM_API_KEY VLLM_USE_RUST_FRONTEND; } 2>/dev/null ||
    { echo 'cannot clear VLLM_API_KEY or VLLM_USE_RUST_FRONTEND in this shell; not starting'; exit 2; }
  grep -Eq '^api-key: "[0123456789abcdef]{64}"$' "$HOME/.config/vllm/server.yaml" ||
    { echo 'no generated api-key line in ~/.config/vllm/server.yaml; not starting'; exit 2; }
  vllm serve 'REPLACE_WITH_MODEL' --host 127.0.0.1 --config "$HOME/.config/vllm/server.yaml"
)
```

The launch block clears `VLLM_API_KEY` first and refuses to start when it cannot (a readonly name in your shell), so an inherited value cannot stand in for the key, and it refuses a file with no generated `api-key` line. It clears `VLLM_USE_RUST_FRONTEND` the same way, because with that opt-in set the pinned server starts a Rust frontend process and hands it the non-default arguments, `api_key` included, as a JSON `--args-json` value on that process's command line. Keep `--config` and the path as two words: the pinned parser expands the file only when `--config` is an argument of its own, and it accepts `--config=FILE` without reading the file, so that server would start with no key. `--host 127.0.0.1` stays on the command line because it is not secret. vLLM merges the file's values into its argument list inside the Python process, and API server processes it starts receive their arguments through Python's `spawn` pipe rather than a command line, so the key stays out of `/proc/<pid>/cmdline` and `ps`. The HTTP server's startup log prints the non-default arguments with `api_key` redacted, but `vllm serve --grpc` logs its whole argument set unredacted, the key included, so protect that log if you use `--grpc`. The key remains in process memory and in the file (plaintext at rest, readable by that account and by root, so keep it and its backups out of source control). Clients read the key from the file's `api-key` line; give remote clients their copy through your secret store ([secrets.md](secrets.md)). A key passed through `VLLM_API_KEY` would stay out of argv but remain readable through `/proc/<pid>/environ` by the same account and by root for the server's whole lifetime, and in any process that inherits it; the file avoids that channel. This was read in the pinned source (cited in Sources). The pinned parser class was also run on its own, outside vLLM, with vLLM's logger stubbed and a minimal `serve` parser in place of vLLM's own: with `--config FILE` it turned the generated file's `api-key` line into a one-element key list, and with `--config=FILE` it left the key unset. No vLLM server was run.

The key does not cover the whole server. vLLM's own security page states that at v0.30.0 it authenticates only the `/v1`, `/v2`, `/inference`, and `/cohere` path prefixes, and lists `/invocations`, the SageMaker-compatible route, as requiring no key while reaching the same inference capability as the protected `/v1` routes; the profiler routes `/start_profile` and `/stop_profile`, available when profiling is enabled via `--profiler-config`, are likewise unauthenticated, and a plugin route outside those prefixes is unauthenticated unless the plugin enforces its own check. vLLM says plainly not to rely on the key alone. Allowlist only the routes your application needs at the proxy and refuse everything else there, `/invocations` included, rather than assuming the key covers the surface. vLLM binds every interface by default: `vllm serve` leaves `--host` unset, which listens on `0.0.0.0` (the startup log shows `http://0.0.0.0:8000`), so pass `--host 127.0.0.1` to keep it on loopback. vLLM can terminate TLS natively (`--ssl-keyfile`, `--ssl-certfile`, and `--ssl-ca-certs`, passed through to uvicorn), but fronting it with a TLS proxy or tunnel is the recommended pattern; either way keep the server itself on loopback or a private network.

### Multi-node and data-parallel deployments

At v0.30.0, `--host` controls the frontend listener, not all the engine's network traffic. Multi-node deployments must run on an isolated network with firewall rules that admit internal traffic only from trusted cluster members. The HTTP API key and frontend TLS do not authenticate or encrypt the internal TCPStore, ZMQ or collective-communication channels. A private IP alone does not establish that isolation. When Ray is the backend, apply [ray.md](ray.md) as well; vLLM treats the Ray cluster as one trust domain.

The listeners depend on the backend and topology:

- vLLM's security page warns that PyTorch TCP initialization creates a TCPStore listening on all interfaces by default; do not infer its bind from the advertised master address. `StatelessProcessGroup.create()` explicitly binds the supplied address on rank zero when no listening socket is supplied; other stateless initialization paths can delegate to ordinary rendezvous. Multi-node multiprocessing uses `--master-addr` and `--master-port` (default port 29501). Data-parallel group initialization can allocate additional ports, and Ray V2 creates a store on port zero. vLLM creates Gloo and device-backend groups; their transport sockets depend on PyTorch and the selected backend and must be inventoried at runtime.
- Engine clients use unauthenticated ZMQ sockets. The multiprocessing DP launch path uses a startup-scoped TCP handshake on `--data-parallel-address` and `--data-parallel-rpc-port` (default port 29550) when engines are remote or elastic expert parallelism is enabled; otherwise the handshake uses IPC. The Ray DP launch path bypasses that handshake constructor. Request/result channels use dynamic TCP ports when clients need remote engines; co-located channels normally use IPC, with an elastic expert-parallelism exception. When online DP needs a coordinator, its frontend and engine channels use IPC or dynamic TCP ports according to locality. The DP address defaults to loopback for the multiprocessing backend unless a master address is supplied; Ray uses the detected node IP. Worker message queues add a dynamic TCP listener only when remote readers exist, using vLLM's detected node IP for multiprocessing and Ray's node IP for Ray V2. `--headless` removes the HTTP frontend, not the internal channels required by that topology.
- KV-transfer listeners are connector-specific and opt-in. The NIXL handshake defaults to `localhost`, port 5600 plus the data-parallel index, and starts when handshake metadata is supplied. Mooncake's producer functionality, including `kv_both`, starts a bootstrap server on `0.0.0.0`, port 8998, at the designated TP/PP/DP rank, and producer worker side channels use the detected node IP and dynamic ports. Consumer-only workers do not start those producer listeners. These vLLM control paths add no peer authentication; this is not an audit of the native transfer libraries. Audit the selected connector and its transfer library; there is no universal KV-transfer bind switch.
- Optional `--grpc` replaces HTTP with an unauthenticated, unencrypted gRPC server on `--host`/`--port`, default `0.0.0.0:8000`. The security page's `--grpc-port` description does not match this release's CLI. `--data-parallel-multi-port-external-lb` also adds a health supervisor after the child servers become ready, without an API-key check, on `--host`, default port 9256 (`--data-parallel-supervisor-port`), alongside one API port per local rank. The supervisor also accepts the frontend TLS options.

Set `VLLM_HOST_IP` to each node's own isolated-network IP; automatic detection can select a public-facing interface and falls back to `0.0.0.0`. Set `--data-parallel-address` to the head node's isolated-network IP and use the same `--data-parallel-rpc-port` on participating nodes. For multi-node multiprocessing, set `--master-addr` to the intended master IP too. `VLLM_PORT` is a starting point for the open-port allocator, not a firewall port range: sockets that bind port zero still receive dynamic ports. `VLLM_DP_MASTER_IP` and `VLLM_DP_MASTER_PORT` populate the environment-driven DP fallback, for example offline SPMD; they are not substitutes for the serving flags. Setting `VLLM_DP_MASTER_PORT` also reserves ten ports starting at that value in the common open-port allocator, so its effects are not confined to offline DP. NIXL has separate `VLLM_NIXL_SIDE_CHANNEL_HOST` and `VLLM_NIXL_SIDE_CHANNEL_PORT` settings; `VLLM_MOONCAKE_BOOTSTRAP_PORT` changes Mooncake's bootstrap port, not its wildcard bind.

Single-GPU serving normally uses a file store and local engine IPC in this release, with a TCP-store exception for ROCm AITER custom all-reduce. This is not a guarantee that no other socket listens: vLLM still creates Gloo groups. Inventory the running processes and test the firewall on single-host deployments too.

## Hugging Face Text Generation Inference (TGI)

`text-generation-launcher` listens on `0.0.0.0:3000` by default (as of v3.3.7; `--hostname`, env `HOSTNAME`; `--port`, env `PORT`). The image built from the repository's main `Dockerfile` sets `PORT=80`, so a bare container listens on port 80 instead, and on every interface: Docker sets `HOSTNAME` to the container's hostname (by default its short ID), which is not an IP address, and the router then falls back to `0.0.0.0`. Bind it to loopback (substitute your model ID inside the quotes in the block below), or publish nothing from the container network except the proxy:

Lifecycle note, as of September 2026: the TGI repository is in maintenance mode and was archived on 2026-03-21 (read-only). Hugging Face recommends vLLM, SGLang, or local engines such as llama.cpp going forward. A server that no longer receives fixes belongs behind the same controls as any other, and on a migration list.

```bash
text-generation-launcher --model-id 'REPLACE_WITH_MODEL_ID' --hostname 127.0.0.1 --port 3000
```

The launcher reference lists `--api-key` (env `API_KEY`) without describing it. At v3.3.7 the launcher takes that value from the flag or from `API_KEY` and then starts the router with it as a `--api-key` argument, so however you supply it, the key is readable through the router process's `ps` and `/proc/<pid>/cmdline` by other local accounts while TGI runs; no launcher input avoids that, and passing it through the environment does not help. TGI's native key is a control for network clients, not for other users of the host: run it where no account you do not trust can list its processes, and enforce the bearer check at the proxy. The router source shows what it does: when set, requests to the standard inference `base_routes` must carry a matching `Authorization: Bearer <key>` header or receive 401, while the health, info, and metrics routes stay unauthenticated. Builds that enable the KServe (`/v2/...`) endpoints register them outside that key middleware, `/v1/models` sits outside it too, and the Vertex feature route configured through `AIP_PREDICT_ROUTE` is registered after the auth layer as well, so those paths are unauthenticated; allowlist the routes you use and enforce the bearer check at the proxy. Treat it as a second layer and enforce the bearer check at the proxy too (pattern in [ollama.md](ollama.md)). The launcher has no TLS option, so front TGI per [nginx.md](nginx.md)/[caddy.md](caddy.md). The Prometheus listener (`--prometheus-port`, default 9000) is unauthenticated as well; keep it private.

## SGLang

`python -m sglang.launch_server` listens on `127.0.0.1:30000` by default (`--host`, `--port`; values as of v0.5.20); keep that bind. `--api-key` sets the key the OpenAI-compatible endpoints require, and `--admin-api-key` separately protects administrative endpoints (at v0.5.20, the weight-update endpoints and `/flush_cache` among them, but not `/server_info`; see below), which then require `Authorization: Bearer <admin key>`. Do not put either value on the command line: there it is readable through `ps` and `/proc/<pid>/cmdline` by other local accounts for the server's whole lifetime. At v0.5.20, `--config` reads the server options from a YAML file instead, and the pinned sources document no stdin or environment input for either key, so put both keys in a file that only the account running SGLang can read. Create it once, as that account:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -eC
  umask 077
  mkdir -p -- "$HOME/.config/sglang"
  chmod 700 -- "$HOME/.config/sglang"
  if [ -e "$HOME/.config/sglang/server.yaml" ] || [ -L "$HOME/.config/sglang/server.yaml" ]; then
    echo 'server.yaml already exists in ~/.config/sglang; nothing written'; exit 2
  fi
  set -- "$(openssl rand -hex 32)" "$(openssl rand -hex 32)"
  [ "${#1}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  [ "${#2}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  case "$1$2" in *[!0123456789abcdef]*) echo 'key generation failed; nothing written'; exit 2 ;; esac
  printf 'api-key: "%s"\nadmin-api-key: "%s"\n' "$1" "$2" > "$HOME/.config/sglang/server.yaml"
)
```

The block writes nothing unless both generated keys are 64 hex characters, because SGLang serves ordinary requests whenever the API key is empty, even when `--admin-api-key` is set, so an empty value would leave the OpenAI-compatible endpoints open. `umask 077` creates the directory mode `0700` and the file mode `0600`. The block makes the directory mode `0700` first and then refuses, before it generates a key, when `server.yaml` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not), so a rerun cannot replace keys your clients already hold; `set -C` also refuses an existing regular file, and the explicit check handles the other forms. These checks hold only in owner-only directories no other account can replace. The keys pass only through the subshell's positional parameters and the builtin `printf`, never a command line; the block clears inherited traps first because a DEBUG, RETURN or ERR trap from your shell could otherwise read them, and it assumes a clean shell. Start the server with only non-secret values on its command line, substituting your model path inside the quotes, and do not add `--api-key` or `--admin-api-key` there, which would put the values back in argv:

```bash
python -m sglang.launch_server --model-path 'REPLACE_WITH_MODEL_PATH' --config "$HOME/.config/sglang/server.yaml"
```

Clients read the API key from the file's `api-key` line; give the admin key only to the operators who use the administrative endpoints. SGLang turns the file's values into an internal argument list before parsing them; that list lives inside the Python process, not in the kernel's `/proc/<pid>/cmdline`, so the keys stay out of `ps`. They remain in process memory and in the file (plaintext at rest, readable by that account and by root, so keep it and its backups out of source control), and SGLang itself hands them out. At v0.5.20 the launch path logs `server_args=` with every resolved field, both keys included, at INFO level, and `/server_info` (and its deprecated alias `/get_server_info`) returns the same fields plus `launch_command`, the argument list with the file's values merged in, to any request the ordinary API key authorizes, because it carries no admin auth level. This was read in the pinned source (cited in Sources), not run. So a holder of the API key can read the admin key. Either give the API key only to clients you would also trust with the administrative endpoints, or, if other clients must hold it, have the reverse proxy allow only the routes those clients need (which excludes `/server_info` and `/get_server_info`) and refuse every other route, the same allowlist the vLLM section prescribes; either way, protect the startup log.

Native TLS exists: `--ssl-keyfile` and `--ssl-certfile` take PEM files ([self-signed.md](self-signed.md) or [free-certificates.md](free-certificates.md)), `--ssl-ca-certs` names a CA bundle, and `--enable-ssl-refresh` hot-reloads renewed certificates. A reverse proxy remains the simpler choice when you already run one.

## NVIDIA Triton Inference Server

`tritonserver` starts three listeners on `0.0.0.0`: HTTP on 8000, gRPC on 8001, and Prometheus metrics on 8002. No authentication is enabled by default: its optional gRPC mutual TLS and restricted-API shared secrets can cover inference as well as model control, but do not replace the gateway. NVIDIA's secure deployment guidance is that Triton is a microservice that is "not exposed directly to an untrusted network": a dedicated gateway or proxy (NGINX, Envoy, Istio, Kong are the examples given) handles authorization, access control, and encryption, and Triton "handles only trusted, validated requests". Bind each listener privately and disable the protocols you do not use:

```bash
tritonserver --model-repository=/models --http-address=127.0.0.1 --grpc-address=127.0.0.1 --metrics-address=127.0.0.1
```

`--allow-http` and `--allow-grpc` default to true; NVIDIA recommends setting either to false when not required, and `--allow-metrics` switches off the metrics listener. For gRPC, `--grpc-use-ssl` with `--grpc-server-cert` and `--grpc-server-key` enables a TLS channel, and `--grpc-use-ssl-mutual` requires client certificates. HTTP has no TLS option; the proxy provides it. `--http-restricted-api` and `--grpc-restricted-protocol` fence the API groups you name (model-repository control, and inference too if you list it) behind a shared-secret header, a useful second layer against network clients but not a substitute for the gateway. The secret is part of the flag's value (`--http-restricted-api=<API_1>,<API_2>:<restricted-key>=<restricted-value>`), and `tritonserver` has no other input for it. Traced at the pinned source commit: `tritonserver` parses its options with `getopt_long` over argv, the two options hand their value straight to the restricted-feature parser, the parser opens no option or response file and reads nothing from stdin, and every environment variable read under `src/` has a non-secret name (the `AIP_*` and `SAGEMAKER_*` endpoint settings, the `OTEL_BSP_*` tracing settings, a gRPC response-delay setting and test-backend names). So the value sits in argv, readable through `ps` and `/proc/<pid>/cmdline` by other local accounts, as well as by the same account and root, for the server's whole lifetime; quoting does not change that, and no `tritonserver` launch form avoids it. Command-line auditing on the host (auditd `EXECVE` records, for example) can also record the value and keep it after the process exits. Under an orchestrator the same value also sits in the workload definition (a Kubernetes pod spec's `args`, for example) for everyone who can read it. A server's shared secret is neither throwaway nor short-lived, so it is no secret from other accounts on the host: do not rely on it as a control against them. Enforce authorization at the reverse proxy or gateway in front of Triton, which is the control, and treat the restricted-API value only as a check against network clients that reach Triton past it; rotate the value whenever an account you do not trust could have read it, or a command-line audit record holding it could have reached one. If you do not load and unload models at run time, leave `--model-control-mode` at its default, `none`, under which the model-control API returns an error for load and unload requests, whatever the secret. Builds with cloud endpoints add conditional listeners beyond these three: `AIP_MODE=PREDICTION` enables a Vertex AI endpoint (its port is `AIP_HTTP_PORT`, otherwise 8080), and a SageMaker endpoint may also be present, so disable the ones you do not use or add them to the bind inventory and the checks below.

At the pinned commit (first shipped in v2.69.0), every restricted category defaults to unrestricted: `health`, `metadata`, `inference`, `shared-memory`, `model-config`, `model-repository`, `statistics`, `trace`, and `logging`. Model control is only one part of that surface. These defaults apply when the corresponding feature is compiled in:

| Category | Exposure without a restriction |
| --- | --- |
| `health`, `metadata`, `inference` | Server/model health and metadata, inference, and HTTP `generate`/`generate_stream` requests need no key. |
| `logging` | Read the log settings and file path; change info/warning/error logging, verbosity, and format. A request cannot change `log_file`. |
| `trace` | Read global or per-model settings, including, in the default `triton` mode, the trace file path; change level, rate, count, and log frequency. A request cannot change `trace_file`. Tracing starts OFF with no file path in the default `triton` mode, so enabling it through the API fails until startup supplies a path, for example `--trace-config triton,file=/var/log/triton/trace.json`. That flag leaves the level OFF; `--trace-config level=TIMESTAMPS` enables it at startup, and an unrestricted client can enable or change it later once the configuration is valid. The settings API itself is not disabled by OFF. |
| `shared-memory` | Read system/CUDA region status. Registration, unregistration, and inference use are disabled by default (`--allow-client-shm=false`); `--allow-client-shm=true` enables them. Clients can then register system shared-memory objects or CUDA IPC handles for tensor input/output and unregister regions. CUDA also requires GPU support; the protocol documentation lists no shared memory on Windows and no CUDA shared memory on Jetson. |
| `model-repository` | List repository models, including unloaded models. Load/reload and unload require `--model-control-mode=explicit`; `none` (default) and `poll` do not enable those API operations. Load accepts a JSON-string `config` override and inline `file:VERSION/FILE` contents (base64 over HTTP, bytes over gRPC, with `config` required); unload can include `unload_dependents=true`. |
| `statistics`, `model-config` | Read per-model/version inference statistics and model configuration. Model control mode does not protect these reads or the repository index. Statistics require a build with statistics support. |

Restrictions are per category and per protocol, not a single admin switch. Repeat a flag for disjoint groups with different keys; a category cannot appear in two groups for the same protocol. This syntax example covers all nine categories with a value held by the gateway, which must not give that administrative value to ordinary inference clients:

```text
--http-restricted-api=health,metadata,inference,shared-memory,model-config,model-repository,statistics,trace,logging:gateway-key=REPLACE_WITH_GATEWAY_VALUE
--grpc-restricted-protocol=health,metadata,inference,shared-memory,model-config,model-repository,statistics,trace,logging:gateway-key=REPLACE_WITH_GATEWAY_VALUE
```

Replace the placeholder through your deployment's secret handling, subject to the argv exposure above. HTTP expects `gateway-key: VALUE`; gRPC expects metadata `triton-grpc-protocol-gateway-key: VALUE`, because Triton prefixes the configured key. Missing or wrong values receive HTTP 403 or gRPC `UNAVAILABLE` with a restriction message. Restricting `health` also requires the header on health probes. These rejections apply to the standard HTTP and gRPC handlers; two cloud endpoints at the pinned commit fall outside them. With the SageMaker listener enabled, a multi-model endpoint's `POST /models/{model}/invoke` runs inference with no restriction check, so gateway authorization and network isolation must cover it, or disable the SageMaker listener. The Vertex AI prediction route dispatches to other handlers named in the `X-Vertex-Ai-Triton-Redirect` request header, `metrics` among them with no restriction check, so a gateway that attaches the administrative value to Vertex prediction requests must strip or reject that header from ordinary clients.

The metrics listener is separate: `GET /metrics` (also `/metrics/`) on 8002 returns Prometheus text with no authentication, and neither restricted flag covers it. Keep it private or use `--allow-metrics=false`. Keep the gateway's route allowlist narrow even when every category is restricted.

## LM Studio (local server)

LM Studio's developer server is a desktop feature. The documentation addresses it at `http://localhost:1234` throughout (the port is a field in Developers Page > Server Settings), and "By default, LM Studio does not require authentication for API requests." The "Serve on Local Network" switch (or `lms server start --bind 0.0.0.0`) rebinds it to every interface; LM Studio's own note reads: "Any bind other than 127.0.0.1 exposes the server beyond localhost; we recommend enabling authentication." Leave that switch off. If another machine must reach it, first enable "Require Authentication" (LM Studio 0.4.0 or newer) and create a token under "Manage Tokens"; clients then send `Authorization: Bearer <token>`. The server settings list no TLS option, so anything beyond the local machine goes through a tailnet ([tailscale.md](tailscale.md)) or an authenticated TLS proxy, never a port-forward.

## text-generation-webui

One process, two surfaces: the Gradio UI (default `127.0.0.1:7860`) and, when started with `--api`, an OpenAI-compatible API (default `127.0.0.1:5000`, endpoints under `/v1`). Both default to loopback, and both start with no authentication.

`--listen` rebinds to `0.0.0.0`, and it widens both surfaces at once: opening the UI to your LAN also opens the API port whenever `--api` is set. `--listen-port` moves the UI port, `--api-port` moves the API port, and `--listen-host` picks a specific bind address instead of `0.0.0.0`; like the wider binding itself it takes effect only with `--listen`, and on its own it does nothing. Never start an internet-adjacent instance with `--share`: it publishes the UI through a public `*.gradio.live` tunnel, reachable by anyone who has the URL. `--public-api` does the same for the API through a Cloudflare tunnel. Treat both flags as publishing, not as remote access.

Auth is per surface, and neither control covers the other:

- UI: `--gradio-auth-path FILE` turns on a Gradio login form from the `user:password` entries in the file; `--gradio-auth user:password` takes the same entries on the command line, where they do not belong (below). Neither does anything for the API.
- API: `--api-key KEY` requires `Authorization: Bearer KEY` on the OpenAI-compatible routes such as `/v1/models` and `/v1/chat/completions`; the Anthropic-compatible `/v1/messages` route reads the same key from an `x-api-key` header instead. `--admin-key` guards the admin endpoints (model load and unload) and falls back to the `--api-key` value when unset; an admin key alone does not protect the ordinary routes. Without `--api-key`, the API answers anyone who can reach the port, even when the UI has a Gradio login in front of it. At the pinned commits, starting the API logs the configured `--api-key` (and any distinct `--admin-key`) in plaintext at INFO level to stdout and the service log, so protect that output as you protect the key file below (owner-only, out of source control and out of shared log collection) and rotate the key after any disclosure.

All three are secrets, and none belongs on the command line, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the server's whole lifetime; quoting does not change that. Put the login in the `--gradio-auth-path` file. At the pinned `server.py` the loader reads `user:password` entries separated by commas or line breaks, strips the whitespace around each, and splits each entry at every `:`, so neither the user name nor the password may contain `:` or `,`. The block below allows only letters, digits, dot, underscore and hyphen in the user name and generates a hex password. Create the file once, as the account that runs text-generation-webui, substituting the user name inside the quotes on the `set --` line:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -eC
  umask 077
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_UI_USER'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; nothing written'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value, inside the quotes; nothing written'; exit 2; }
  case "$1" in ""|*REPLACE_WITH_*) echo 'substitute a user name inside the quotes on the set -- line above; nothing written'; exit 2 ;; esac
  case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]*) echo 'use only letters, digits, dot, underscore or hyphen in the user name; nothing written'; exit 2 ;; esac
  mkdir -p -- "$HOME/.config/text-generation-webui"
  chmod 700 -- "$HOME/.config/text-generation-webui"
  if [ -e "$HOME/.config/text-generation-webui/gradio-auth" ] || [ -L "$HOME/.config/text-generation-webui/gradio-auth" ]; then
    echo 'gradio-auth already exists in ~/.config/text-generation-webui; nothing written'; exit 2
  fi
  set -- "$1" "$(openssl rand -hex 16)"
  [ "${#2}" -eq 32 ] || { echo 'password generation failed; nothing written'; exit 2; }
  case "$2" in *[!0123456789abcdef]*) echo 'password generation failed; nothing written'; exit 2 ;; esac
  printf '%s:%s\n' "$1" "$2" > "$HOME/.config/text-generation-webui/gradio-auth"
)
```

The `set --` line opens with a marker the block checks, so a paste that drops that line is refused rather than run on your shell's own arguments. The block makes the directory mode `0700` first, then refuses, before it generates a password, when `gradio-auth` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not); as with the vLLM block, that holds only in owner-only directories no other account can replace. `umask 077` creates the directory mode `0700` and the file mode `0600`, `set -C` still refuses to overwrite an existing regular file, and the block writes nothing unless the generated password is 32 hex characters. The password passes only through the subshell's positional parameters and the builtin `printf`; the block clears inherited traps first and assumes a clean shell. Read the password from the file once into your password manager. The file holds it in plaintext at rest, readable by that account and by root, so keep it and its backups out of source control.

The API keys have no file flag and no environment input at the pinned sources: the API reads them only from the parsed arguments. The pinned `modules/shared.py` does read further flags from `CMD_FLAGS.txt` in the user-data directory, and it splices them into Python's own argument list inside the process, so keys placed there stay out of `/proc/<pid>/cmdline`. Do not use the checkout's own `user_data/CMD_FLAGS.txt` for them: at the pinned commit it is a tracked file (it ships with three comment lines), so a key written there is a change to a tracked file that `git diff` prints and `git stash` copies into the repository, and the update wizard in `one_click.py` runs `git merge --autostash` (stashing the change) and offers `git reset --hard` (discarding it). This was read from the code, not run. Point `--user-data-dir` at a private directory outside the checkout instead, readable only by the account that runs text-generation-webui; it then stands in for the whole `user_data` directory (the model, LoRA and cache directories, among others, default under it), so copy across the models and settings you use. Write generated keys into a new `CMD_FLAGS.txt` there, as that account, substituting the directory's absolute path inside the quotes on the `set --` line (a path with spaces stays one value there). Write each `'` in the path as `'\''`; this is required, because a `'` left unescaped or escaped wrongly ends the quoting early, and the rest of the line can then change the path the block uses or run as shell syntax:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -eC
  umask 077
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PRIVATE_USER_DATA_DIR'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; nothing written'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value, inside the quotes; nothing written'; exit 2; }
  case "$1" in ""|*REPLACE_WITH_*) echo 'substitute the private user-data directory inside the quotes on the set -- line above; nothing written'; exit 2 ;; esac
  case "$1" in /*) ;; *) echo 'give the user-data directory as an absolute path; nothing written'; exit 2 ;; esac
  mkdir -p -- "$1"
  cd -- "$1"
  chmod 700 .
  (
    while :; do
      if [ -e .git ] || [ -L .git ]; then exit 3; fi
      if [ . -ef .. ]; then exit 0; fi
      cd -P .. || exit 4
    done
  ) || { echo 'that directory or one above it holds a .git entry, or the walk could not reach /; no key written'; exit 2; }
  if [ -e CMD_FLAGS.txt ] || [ -L CMD_FLAGS.txt ]; then
    echo 'CMD_FLAGS.txt already exists there; use a new private directory; no key written'; exit 2
  fi
  set -- "$(openssl rand -hex 32)" "$(openssl rand -hex 32)"
  [ "${#1}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  [ "${#2}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  case "$1$2" in *[!0123456789abcdef]*) echo 'key generation failed; nothing written'; exit 2 ;; esac
  printf -- '--api-key %s\n--admin-key %s\n' "$1" "$2" > CMD_FLAGS.txt
)
```

The block creates `CMD_FLAGS.txt` once and never appends to one. Its `set --` line opens with a marker the block checks, so a paste that drops that line is refused rather than run on your shell's own arguments. Before it generates a key, it refuses a relative path; a directory that holds a `.git` entry of any kind, or has one in any directory above it, whether a repository directory, a submodule's or worktree's `.git` file, a symlink or a malformed entry, which covers the checkout's own `user_data`; and a directory where `CMD_FLAGS.txt` already exists in any form, a dangling symlink included. The walk starts in the target directory and steps up with `cd -P ..` until `.` and `..` are the same directory, testing `.git` relative to each one, so symlinks are resolved and no path string is built: a newline or other unusual byte in a directory name, or a physical path longer than the system's path limit, cannot hide an ancestor's `.git`. It refuses if any step fails. The walk does not run git, so neither a git error nor an inherited `GIT_*` variable can let the write through. It cannot see a checkout reached through a bind mount, or a repository whose work tree is set elsewhere (a bare "dotfiles" repository used with `--work-tree=$HOME`, for example), so choose a directory you know is outside any checkout. Like the other writers' checks, the walk and the existence check run before the write, not atomically with it, so they hold only in owner-only directories no other account can change, and a `.git` created there between the check and the write is not seen. A directory the block refuses after entering it is left behind, empty if the block created it, and mode `0700`. The block makes the directory mode `0700` after entering it, so for a directory another account owns `chmod` itself fails and the block stops there, with `chmod`'s error rather than its own message and the directory's mode unchanged; run as root, that `chmod` succeeds on any directory, so do not run the block as root. `umask 077` creates the file mode `0600`, `set -C` also refuses an existing regular file (the explicit check handles the other forms), and the block writes nothing unless both keys are 64 hex characters. The keys pass only through the subshell's positional parameters and the builtin `printf`. Add any other flags you want in the file on new lines after the two key lines, and never add or edit a key line: the loader joins the file's lines before splitting them into arguments, and a later `--api-key` or `--admin-key` would silently replace a key. To rotate the keys, run the block again with a new private directory and move your settings across. Start `server.py` from the installation directory with only non-secret values on its command line, substituting the same path inside the quotes:

```bash
python server.py --user-data-dir 'REPLACE_WITH_PRIVATE_USER_DATA_DIR' --api --gradio-auth-path "$HOME/.config/text-generation-webui/gradio-auth"
```

Start it this way, directly, not through the one-click `start_*` scripts. At the pinned `one_click.py` the launcher joins its own arguments into one string without quoting them (line 24), builds `python server.py` plus that string (line 486) and runs the result through `bash` with `shell=True` (line 208), so a quoted path is split at its spaces and any shell syntax in it runs, and a key passed to those scripts would land on `server.py`'s command line again. This was read in the pinned source, not run. Clients read the API key from the file's `--api-key` line; give the admin key only to the operators who load and unload models. The keys remain in process memory, in the file, and in the startup log (above). The pinned `modules/shared.py`, imported with `--user-data-dir` pointing at a directory the block had written (a path containing a space, with a `--listen-port` line added after the key lines), parsed both keys and that flag from `CMD_FLAGS.txt` while the process's `/proc/self/cmdline` held neither; the launcher and API behaviour above was read in the pinned source (cited in Sources), and no text-generation-webui server was run.

`--api --nowebui` runs the API alone, the right shape for a server where the UI has no business existing. `--ssl-keyfile` and `--ssl-certfile` give both surfaces TLS, but the better pattern is the usual one: keep both ports on loopback and front them with a reverse proxy that terminates TLS and enforces auth (`--subpath` exists for serving the UI under a proxy path). Without TLS, the Gradio login submits credentials in the clear.

One proxy detail is specific to this API: unless `--listen` (or `--public-api`) is set, it rejects any request whose `Host` header is not `localhost` or `127.0.0.1` with a `400`, so a reverse proxy in front of a loopback API must send `Host: localhost` upstream rather than forwarding the public hostname.

## The pattern, whatever the server

1. Bind to `127.0.0.1` (or a private container network); confirm with `ss -tlnp`.
2. Require a per-client API key at the server where supported, or at the proxy otherwise (bearer-token check per [ollama.md](ollama.md)); generate keys per [authentication.md](authentication.md). Keep the key off the server's command line, child processes included: use stdin where the server offers it, otherwise a file the server reads itself, created owner-only, or the guarded one-command prefix assignment of CONTRIBUTING rule 7, which leaves the key readable through `/proc/<pid>/environ` for the server's lifetime. Where the server takes the secret only in argv (the TGI router's key, Triton's restricted-API value), its native check is a control against network clients, not against other local accounts; enforce auth at the proxy.
3. TLS in front: [caddy.md](caddy.md), [nginx.md](nginx.md), [cloudflare.md](cloudflare.md), or [tailscale.md](tailscale.md).
4. Human-facing UIs on top of these servers ([open-webui.md](open-webui.md)) carry their own login and MFA ([mfa.md](mfa.md)).

## Verify

**REASONED:** following block; service checks follow the cited server handlers and need unavailable live servers/proxy fixtures. Only the pgrep subcheck has the recorded stub-process demonstration below; the whole mixed block remains REASONED.

```bash
ss -tlnp   # every listener; 8080/8000/8001/8002/3000/80/9000/30000/5000/7860/1234. ss shows only a
           # namespace-local BIND, not a host firewall, a cloud security group, or Docker -p NAT
           # publication. From another host, probe EACH backend listener's own host and port (adapt the
           # subshell below, which shows the technique for one endpoint) and confirm each is refused
pgrep -c -f -- '(^| )--((admin-)?api-key|admin-key|gradio-auth|http-restricted-api|grpc-restricted-protocol)( |=)'
           # counts visible command lines carrying one of those secret-bearing arguments; 0 means none was seen
           # right now, and any match needs a look. Triton's restricted-API secrets have no input outside the
           # flag value, so a match is expected while you use them. It does not see a key in a file the server
           # reads, in a server's environment (VLLM_API_KEY, LLAMA_API_KEY), inside another argument's value
           # (vLLM's Rust-frontend --args-json), on an abbreviated option that argparse or getopt_long accepts
           # (--api-k X, --http-restricted=...), or on a flag the pattern does not name
(
  # Feed the API key to curl on stdin (curl --header @-), never in argv:
  # -H "Authorization: Bearer KEY" is readable in ps / /proc/<pid>/cmdline.
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The API key you substitute on the set -- line enters shell history.
  # Use a short-lived key or clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_API_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the API key on the set -- line above; not probing"; exit ;; esac
  curl -q -sS --noproxy '*' -w 'http=%{http_code} exit=%{exitcode}\n' https://models.example.com/v1/models   # PROXY-policy test: 401 without a key. TGI leaves /v1/models outside its native key middleware, so a 200 is not proof the backend enforces the key
  printf 'Authorization: Bearer %s\n' "$1" | curl -q -sS --noproxy '*' -w 'http=%{http_code} exit=%{exitcode}\n' -H @- https://models.example.com/v1/models   # positive control: 200 with a model list, printed
)
(
  set -- 'REPLACE_WITH_A_REAL_SERVED_MODEL'
  case "$1" in ""|*REPLACE_WITH_*) echo 'substitute a real served model name inside the quotes on the set -- line above; not probing'; exit 2 ;; esac
  curl -q -sS --noproxy '*' -D - -o invocations-body.txt -w 'http=%{http_code}\n' -X POST -H 'Content-Type: application/json' \
    -d "{\"model\":\"$1\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" https://models.example.com/invocations
)
                                                        # vLLM /invocations needs JSON (a bare -d '{}' sends form
                                                        # content-type and fails the schema) and a REAL served model.
                                                        # Read the printed headers and saved body, not the status alone: an
                                                        # exposed vLLM given an unknown model also returns 404, so
                                                        # http=404 is AMBIGUOUS with the proxy's own denial. A
                                                        # vLLM-originated reply (200, or a JSON error body) means the
                                                        # route is reachable without the key; a 403/404 only proves
                                                        # denial if the PROXY rejected BEFORE forwarding (its route config
                                                        # or correlated upstream/backend logs) - a proxy that intercepts an
                                                        # upstream error (nginx proxy_intercept_errors) serves its own page
                                                        # while the no-key request reached vLLM, which is reachability, not
                                                        # denial. Treat anything ambiguous as inconclusive
```

The `pgrep` line counts processes whose visible command line has an argument that is `--api-key`, `--admin-api-key`, `--admin-key`, `--gradio-auth`, `--http-restricted-api` or `--grpc-restricted-protocol` followed by a space or `=`, the forms in which llama-server, vLLM, SGLang, the TGI router, text-generation-webui and Triton take a secret on the command line; it prints a count and never a key, and it excludes itself. A count is a lead, not proof: an empty value, or an argument of unrelated text that contains ` --api-key `, matches too, and `0` means only that no visible process matched at that moment. It was demonstrated on the authoring host against stub processes that opened no listener (`python3` sleeping with the test arguments, procps-ng 4.0.4): `--api-key DUMMY_NOT_A_SECRET`, `--admin-key DUMMY_NOT_A_SECRET`, `--admin-api-key=DUMMY_NOT_A_SECRET`, `--gradio-auth u:DUMMY_NOT_A_SECRET`, `--http-restricted-api=model-repository:admin-key=DUMMY_NOT_A_SECRET`, `--grpc-restricted-protocol=model-repository:admin-key=DUMMY_NOT_A_SECRET` and an empty `--api-key=` each counted `1`, while `--api-key-file /x`, `--gradio-auth-path /x`, `--config /x`, `notes--api-key x`, `--admin-keys x`, `--http-restricted-api-x y`, `--args-json '{"api_key":["DUMMY_NOT_A_SECRET"]}'`, and the abbreviations `--api-k DUMMY_NOT_A_SECRET` and `--http-restricted=model-repository:k=DUMMY_NOT_A_SECRET` each counted `0`, so the line tells the file-based launch forms from the argv ones, and it misses a key inside a JSON argument or behind an abbreviated option (the pinned text-generation-webui parser keeps argparse's default prefix matching, and Triton's `getopt_long` accepts an unambiguous prefix). No model server was run for it. A `hidepid` proc mount limits the count to your own processes, and a process that has scrubbed its own arguments is not seen.

For text-generation-webui, ask the API edge for the model list without a key. This step is reasoned, not demonstrated: the authoring environment has no container runtime to stand up a live instance, so the expected `401` is derived from the bearer-token check in `modules/api/script.py` (cited in Sources), not observed. The block prints the `exitcode` and `errormsg` write-out variables, which need curl 7.75.0 or newer. A `200` with a model list means the API is open to anyone; a `401` means the key is enforced. A transfer error is inconclusive: a TLS failure (`exit=35` or `exit=60`) in particular means something did answer, since the API serves plain HTTP unless `--ssl-keyfile`/`--ssl-certfile` are set, so read the `exit` and `err` fields, fix any DNS, TLS, or client cause, and confirm the API listener's own address and port directly from the intended vantage. A `400` carrying `Invalid host header` is the API rejecting the forwarded `Host` (see the reverse-proxy note above), not an authentication result, and a rejection page from your proxy proves only the proxy.

```bash
# REASONED: text-generation-webui authentication follows the cited modules/api/script.py; no container runtime is available.
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host on the set -- line above; not probing" ;;
    *) curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1/v1/models" ;;
  esac
)
```

For Triton, this read checks the `logging` restriction directly on the server host. **REASONED, not demonstrated:** no Triton server, container runtime, or GPU is available in the authoring environment. On an isolated instance with logging support, run it before and after applying the restriction above. Before, expect HTTP 200 with settings JSON containing `log_file` and `log_verbose_level`; after, expect HTTP 403 with `This API is restricted, expecting header 'gateway-key'`. These outcomes follow from the [logging handler](https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L2031-L2149) and [restriction check](https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L4939-L4953). Use the same address and port for both runs. This command assumes Triton's HTTP listener is on loopback port 8000 and needs curl 7.75.0 or newer. A connection error, a proxy rejection, 404, or a logging-unsupported response is inconclusive; a failing request alone is not a pass. This checks only logging over HTTP, not the other categories, gRPC, or external listener isolation. The existing `pgrep` check measures argv exposure, not API authorization.

```bash
# REASONED: Triton logging restriction follows the pinned logging handler and restriction check; no server, runtime, or GPU is available.
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  http://127.0.0.1:8000/v2/logging
```

### vLLM internal-listener isolation (REASONED: cited v0.30.0 listener constructors; no multi-node cluster)

**REASONED, not demonstrated:** no multi-GPU or multi-node cluster is available in the authoring environment. The expected distinction follows from v0.30.0's [internal-network warning and firewall guidance](https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L109-L138) and the listener constructors cited below. No vLLM server was run for this addition.

On every node, run `sudo ss -tlnp` in the host and service network namespaces, during startup and after the engines become ready. Record each vLLM, worker and backend listener, including dynamically assigned ports; re-inventory after a restart. Check container publications and cloud firewall rules too. A private bind or an absent startup-only handshake is not proof that the remaining ports are isolated.

For each endpoint intended for cross-node traffic, run this block in `remote` mode from a trusted cluster peer and then from a host outside the allowed cluster network. Substitute the actual numeric node address reachable from that vantage and the observed port inside the existing quotes on the `set --` line; use the node endpoint, not the API proxy.

For a deliberately loopback-only endpoint, such as a NIXL handshake left on localhost, first run the same block in `local` mode from the listener's own network namespace, substituting its observed numeric loopback address and port. Confirm with the socket inventory that the process binds only the intended loopback addresses, and check that no container publication or forwarding rule exposes it. Then run in `remote` mode from both remote vantages against the node's non-loopback addresses and corresponding ports, including any mapped ports found in the inventory. Do not widen a bind to obtain a remote positive control. Change the mode inside its existing quotes too. The block only attempts a TCP connection and sends no application payload:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'remote' 'REPLACE_WITH_TARGET_IP' 'REPLACE_WITH_INTERNAL_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'the set -- line needs exactly 3 values; not probing'; exit 2; }
  case "$1$2$3" in
    *REPLACE_WITH_*) echo 'substitute the target IP and port; not probing'; exit 2 ;;
  esac
  python3 - "$@" <<'PYPROBE'
import ipaddress
import socket
import sys

try:
    mode = sys.argv[1]
    if mode not in ("remote", "local"):
        raise ValueError("mode must be remote or local")
    address = ipaddress.ip_address(sys.argv[2])
    effective_address = getattr(address, "ipv4_mapped", None) or address
    port = int(sys.argv[3])
    if effective_address.is_unspecified or not 1 <= port <= 65535:
        raise ValueError("use an observed listener address and a valid port")
    if mode == "remote" and effective_address.is_loopback:
        raise ValueError("remote mode needs the non-loopback node IP")
    if mode == "local" and not effective_address.is_loopback:
        raise ValueError("local mode needs the listener's loopback IP")
except ValueError as exc:
    sys.exit(f"Invalid target; not probing: {exc}")
try:
    with socket.create_connection((str(address), port), timeout=5):
        print("CONNECTED: this internal listener is reachable from this host")
except OSError as exc:
    sys.exit(f"NO CONNECTION: {exc}; inconclusive without the paired control")
PYPROBE
)
```

For cross-node endpoints in an intentionally exposed test deployment, the outside probe should report `CONNECTED`. After isolation, the trusted peer must still connect while the outside probe reports `NO CONNECTION`; confirm that firewall logs or counters attribute the latter to the intended rule. For deliberately loopback-only endpoints, the positive control is `CONNECTED` from the same network namespace; both remote probes should report `NO CONNECTION`, supported by the confirmed loopback binds and absence of forwarding. A remote connection to such an endpoint exposes it; a trusted peer is not expected to connect. Where a firewall also blocks a tested path, collect its rule evidence. A negative remote result alone proves neither bind isolation nor firewall enforcement. A stopped process, changed dynamic port, wrong address, routing failure or local socket error is inconclusive. Capture the handshake while it is listening during startup. This checks TCP reachability only; verify any RDMA or other non-TCP transport separately with the selected backend's tools.

## Sources (checked September 2026)

- llama.cpp server README (defaults, `--api-key` and its `LLAMA_API_KEY` environment input, `--api-key-file` ("path to file containing API keys, one per line") and its `LLAMA_ARG_API_KEY_FILE` environment input, the `LLAMA_ARG_*` environment inputs most options carry, `LLAMA_ARG_HOST` for `--host` among them, SSL flags): https://github.com/ggml-org/llama.cpp/blob/e0dff58475bc9ed68eedcb265ee998f2fcabb3b1/tools/server/README.md
- vLLM documentation: https://docs.vllm.ai/
- vLLM v0.30.0 network isolation, TCPStore warning and Ray trust model: https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L3-L55, https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L109-L138 and https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L442-L538
- vLLM v0.30.0 node-address detection, open-port allocator and unauthenticated ZMQ socket construction: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/utils/network_utils.py#L34-L73, https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/utils/network_utils.py#L166-L247 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/utils/network_utils.py#L310-L368
- vLLM v0.30.0 engine IPC/TCP addresses, handshake and DP coordinator: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/engine/utils.py#L1039-L1084, https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/engine/utils.py#L1130-L1247 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/engine/coordinator.py#L79-L97; Ray V2 dynamic store: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/ray_executor_v2.py#L127-L139
- vLLM v0.30.0 DP flags and headless deployment examples: https://github.com/vllm-project/vllm/blob/v0.30.0/docs/serving/data_parallel_deployment.md#L31-L74; headless execution: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/cli/serve.py#L215-L253
- vLLM v0.30.0 parallel configuration defaults and initialization: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/config/parallel.py#L100-L330 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/config/parallel.py#L890-L960; serving address selection: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/engine/arg_utils.py#L2310-L2336
- vLLM v0.30.0 TCP/file rendezvous and stateless stores: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/parallel_state.py#L1793-L1880 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/utils.py#L467-L506 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/utils.py#L634-L647; remote message-queue bind: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/device_communicators/shm_broadcast.py#L519-L537; backend address selection: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/multiproc_executor.py#L148-L169 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/ray_executor_v2.py#L327-L336
- vLLM v0.30.0 single-GPU file-store path and Gloo group creation: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/v1/executor/uniproc_executor.py#L77-L88, https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/utils/network_utils.py#L135-L147 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/parallel_state.py#L494-L508
- vLLM v0.30.0 environment settings for node IP/ports, offline DP and connector side channels: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/envs.py#L701-L715, https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/envs.py#L1433-L1445 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/envs.py#L1650-L1680
- vLLM v0.30.0 NIXL handshake address and listener: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_scheduler.py#L75-L79 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/nixl/base_scheduler.py#L299-L382; Mooncake bootstrap and worker listeners: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L948-L1035 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L1160-L1187; producer worker activation: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L1793-L1801; bootstrap rank selection and port: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/distributed/kv_transfer/kv_connector/v1/mooncake/mooncake_connector.py#L2261-L2296
- vLLM v0.30.0 gRPC selector and insecure bind: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/cli_args.py#L424-L429 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/grpc_server.py#L87-L118; DP supervisor routes and bind: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/dp_supervisor.py#L118-L132, https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/dp_supervisor.py#L220-L238 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/dp_supervisor.py#L322-L349; supervisor activation: https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/cli/serve.py#L85-L95 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/cli/serve.py#L145-L148
- vLLM v0.30.0 frontend defaults (`host=None`, port 8000; unchanged, checked 2026-09-26): https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/cli_args.py#L256-L266
- vLLM v0.30.0 frontend socket bind (unset host binds every IPv4 interface; unchanged, checked 2026-09-26): https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/launcher.py#L211-L225 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/launchers/launcher.py#L270-L288
- vLLM v0.30.0 API key scope (including `/cohere`), unprotected `/invocations` and profiler routes: https://github.com/vllm-project/vllm/blob/v0.30.0/docs/usage/security.md#L140-L247 and https://github.com/vllm-project/vllm/blob/v0.30.0/vllm/entrypoints/serve/middleware/authenticate.py#L11-L62
- vLLM `--api-key` (`FrontendArgs.api_key`, a list of keys; read in source, not run): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/cli_args.py#L304 and https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/entrypoints/launchers/cli_args.py#L296
- vLLM `VLLM_API_KEY`, declared in `envs.py` (https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/envs.py#L803, https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/envs.py#L801) and read as the fallback when `--api-key` is unset, the CLI taking precedence (identical at both commits): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/serve/middleware/register.py#L32-L36
- vLLM `--config` YAML loader (expanded only when `--config` is its own argument, `.yaml` or `.yml` required, `yaml.safe_load`, each key turned into the option `--<key>` and merged into the in-process argument list before parsing): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/utils/argparse_utils.py#L329-L330, #L517-L548, #L585-L596 and #L621-L622
- vLLM startup log of non-default arguments with `api_key` redacted (https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/serve/utils/api_utils.py#L271-L286), and the unredacted `--grpc` argument log: https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/grpc_server.py#L64
- vLLM API server processes started through `multiprocessing` `spawn`, arguments pickled rather than on a command line (https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/v1/utils.py#L210-L246), and the opt-in Rust frontend, started only when `VLLM_USE_RUST_FRONTEND` is set, which receives the non-default arguments, `api_key` included, as `--args-json` on its command line: https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/v1/utils.py#L384-L411 and https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/cli/serve.py#L63-L64
- TGI launcher arguments (--hostname, --port, --api-key, --prometheus-port): https://huggingface.co/docs/text-generation-inference/reference/launcher
- TGI launcher `hostname` default `0.0.0.0` and `port` default 3000, each also read from the environment (pinned tag v3.3.7, the last release before the repository was archived): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/launcher/src/main.rs#L769-L774
- TGI image built from the repository's main `Dockerfile`, `ENV ... PORT=80` (pinned tag v3.3.7): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/Dockerfile#L147-L149
- TGI router: a `--hostname` that does not parse as an IP address logs "Invalid hostname, defaulting to 0.0.0.0" and binds `0.0.0.0` (pinned tag v3.3.7): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/router/src/server.rs#L1906-L1910
- TGI router source (what --api-key enforces): https://github.com/huggingface/text-generation-inference/blob/24ee40d143d8d046039f12f76940a85886cbe152/router/src/server.rs
- TGI repository (maintenance-mode notice, archived 2026-03-21): https://github.com/huggingface/text-generation-inference
- SGLang server arguments (--host, --port, --api-key, --admin-api-key, SSL flags; docs.sglang.ai redirects here): https://docs.sglang.io/docs/advanced_features/server_arguments
- Triton secure deployment considerations: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/deploy.html
- Triton listener defaults: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.h#L191-L219 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.h#L51-L67
- Triton gRPC TLS flags and restricted protocols: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L558-L576 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L632-L640
- Triton command line parser (HTTP address and port, restricted APIs): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L477-L516
- Triton cloud endpoints outside the restriction flags (commit 546a78766fb112128aa0b10a70c55f4f39c3b1df): the SageMaker multi-model invoke dispatch, which reaches inference without a restriction check, and the Vertex AI redirect header with its unrestricted `metrics` target: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/sagemaker_server.cc#L198-L225, https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/vertex_ai_server.cc#L34-L37, https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/vertex_ai_server.cc#L142-L145 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/vertex_ai_server.cc#L245-L272; shared-memory platform limits: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_shared_memory.md#L65-L68
- Triton `--http-restricted-api` and `--grpc-restricted-protocol`, parsed from argv by `getopt_long` only (traced at 546a787 across `src/`: the option definitions, the parse loop and the two cases handing `optarg` to `ParseRestrictedFeatureOption`, no option or response file, and every `getenv`/`GetEnvironmentVariableOrDefault` under `src/` reading a non-secret name): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L508-L516, #L632-L640, #L1329-L1330, #L1420-L1423 and #L1561-L1566
- Triton category names and initially unrestricted state: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/restricted_features.h#L37-L112
- Triton HTTP route patterns and dispatch: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L1140-L1149 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L4786-L4885
- Triton dynamic logging (mutable settings, file-path disclosure, refusal to change the file path): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L2031-L2149
- Triton trace settings API and file-path refusal: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L1759-L2027; defaults: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.h#L180-L188; runtime updates and file-path requirement: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/tracer.cc#L221-L232 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/tracer.cc#L1244-L1249; startup trace flags: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L739-L750, https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L2247-L2278 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L2297-L2312
- Triton client shared memory (disabled by default, opt-in flag, platform limits): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_shared_memory.md#L29-L68; status and mutation handlers: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L2177-L2378
- Triton repository index and inline load overrides: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_model_repository.md#L59-L90, https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_model_repository.md#L136-L152 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/docs/protocol/extension_model_repository.md#L350-L400
- Triton model configuration and statistics reads: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L1684-L1755; generation routes use the inference restriction: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L3324-L3334
- Triton restriction grouping/parser: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L2095-L2163; gRPC header prefix: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.h#L47-L49; HTTP rejection: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L4939-L4953; gRPC rejection: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/grpc/grpc_server.cc#L194-L225
- Triton metrics path and unauthenticated Prometheus handler: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.h#L143-L157 and https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/http_server.cc#L308-L345; metrics controls: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L708-L725
- Triton model control modes (`none` by default, repository polling under `poll`, API load/unload under `explicit`): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L424-L434
- LM Studio local server: https://lmstudio.ai/docs/developer/core/server
- LM Studio serve on local network: https://lmstudio.ai/docs/developer/core/server/serve-on-network
- LM Studio server settings: https://lmstudio.ai/docs/developer/core/server/settings
- LM Studio authentication: https://lmstudio.ai/docs/developer/core/authentication
- LM Studio OpenAI compatibility (localhost:1234 examples): https://lmstudio.ai/docs/developer/openai-compat
- text-generation-webui README, command-line flags: https://github.com/oobabooga/text-generation-webui#command-line-flags
- text-generation-webui, OpenAI-compatible API documentation: https://github.com/oobabooga/text-generation-webui/blob/ceade2eb1ba3f84518076270df2240b6bbb01da0/docs/12%20-%20OpenAI%20API.md
- text-generation-webui, flag definitions and defaults (modules/shared.py): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/shared.py
- text-generation-webui, `--user-data-dir` and the in-process `CMD_FLAGS.txt` loader (lines whose first non-space character is `#` skipped, the rest split as shell words and spliced into Python's `sys.argv` before parsing): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/shared.py#L50 and #L221-L236, with the directory resolved at https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/paths.py#L5-L21
- text-generation-webui, `user_data/CMD_FLAGS.txt` shipped as a tracked file of three comment lines: https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/user_data/CMD_FLAGS.txt
- text-generation-webui one-click launcher (its own arguments joined unquoted and run through `bash` as `server.py`'s command line, the update wizard's `git merge --autostash` and `git reset --hard`; read in source, not run): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/one_click.py#L24, #L208, #L396, #L485-L486, #L504 and #L527
- text-generation-webui `--gradio-auth-path` loader (entries split at commas and line breaks, whitespace stripped, each split at every `:`): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/server.py#L90-L95
- text-generation-webui, API bind and key checks (modules/api/script.py): https://github.com/oobabooga/text-generation-webui/blob/619a2b8ee4b7e48541a9be5c07e04cd31b91b44f/modules/api/script.py
- text-generation-webui, the API key and a distinct admin key logged in plaintext at INFO at startup: https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/api/script.py#L594-L597 and https://github.com/oobabooga/text-generation-webui/blob/619a2b8ee4b7e48541a9be5c07e04cd31b91b44f/modules/api/script.py#L599-L602
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- SGLang `host` and `port` field defaults, `127.0.0.1` and `30000` (pinned tag v0.5.20; that the `--host`/`--port` flags use these fields rests on the server-arguments docs above): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/arg_groups/fields/serving.py#L72-L73
- SGLang `--config` ("Read CLI options from a config file. Must be a YAML file with configuration options."; pinned tag v0.5.20): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/server_args.py#L397-L399
- SGLang configuration loader (`yaml.safe_load`, a `.yaml` or `.yml` suffix required, each key turned into the option `--<key>` and the values merged into the argument list before parsing; pinned tag v0.5.20): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/utils/server_args_config_parser.py#L118-L187
- SGLang environment registry, checked for an API-key or admin-key entry and found to carry none (pinned tag v0.5.20): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/environ.py
- SGLang key exposure at v0.5.20 (read in source, not run): the `api_key` and `admin_api_key` fields (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/arg_groups/fields/serving.py#L155-L162), `resolved_dict` over every field and `_launch_command` joined from the merged argument list (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/server_args.py#L311-L325 and #L736), the INFO log of `server_args=` (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/entrypoints/engine.py#L1109), `/server_info` with no `auth_level` decorator (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/entrypoints/http_server.py#L818-L850) and a normal endpoint requiring only the API key (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/utils/auth.py#L145-L151)
- TGI launcher: `api_key` is `#[clap(long, env)]`, and the launcher pushes `--api-key` and the value into the router's arguments (pinned tag v3.3.7): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/launcher/src/main.rs
