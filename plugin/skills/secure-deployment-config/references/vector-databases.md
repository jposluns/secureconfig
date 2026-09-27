---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "22588d2b174b781bc11496e54659ec13f08dc6fb50d32d3e28820c70615f55c2",
  "components": {
    "q": {
      "name": "Qdrant source",
      "basis": "v1.19.1",
      "sources": {
        "s7548c65a0e83": "https://github.com/qdrant/qdrant/blob/v1.19.1/src/settings.rs#L292-L329",
        "sd309f5848ac4": "https://github.com/qdrant/qdrant/blob/v1.19.1/config/config.yaml#L330-L334",
        "s6b9ad7f6f7ac": "https://github.com/qdrant/qdrant/blob/v1.19.1/config/development.yaml#L13-L15",
        "sc0a948c10fcb": "https://github.com/qdrant/qdrant/blob/v1.19.1/config/production.yaml#L3-L5",
        "s6463d266f693": "https://github.com/qdrant/qdrant/blob/v1.19.1/Dockerfile#L225-L246",
        "sfbd6a604b16a": "https://github.com/qdrant/qdrant/blob/v1.19.1/tools/entrypoint.sh#L21"
      }
    },
    "qd": {
      "name": "Qdrant security documentation",
      "basis": "unknown",
      "sources": {
        "s753402e46eed": "https://qdrant.tech/documentation/security/"
      }
    },
    "w": {
      "name": "Weaviate source",
      "basis": "v1.39.6",
      "sources": {
        "s8c45722d725f": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/config_handler.go#L1305-L1340",
        "sb916723717de": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L1898-L1914",
        "s7c30e1e2c554": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L1926-L1942",
        "s85b7b3e8fa18": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L1050-L1054",
        "s8c05965785ea": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L2145-L2188",
        "s4d2b119da409": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/grpc/server.go#L475-L477",
        "sa1cbcde2f024": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L47-L53",
        "s122708a42282": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L89-L90",
        "s5b7738072d06": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L97-L100",
        "s71035079ef45": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L303-L310",
        "s7b8a55a31a45": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L345-L349",
        "sc6fc7e030ce0": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/embedded_spec.go#L39-L41",
        "se5771dfe00cc": "https://github.com/weaviate/weaviate/blob/v1.39.6/Dockerfile#L57-L63",
        "sd53f51213b12": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/handlers_debug_gate.go#L23-L33",
        "sae4bd165c1f1": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L329-L336",
        "s3d7fe59cb2c4": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L223-L275",
        "sc1473599ecd1": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L2613-L2657",
        "s909e461943ae": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L95-L98",
        "s8c15def0d8e9": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/cluster/state.go#L431-L446",
        "sc8c8851851c6": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/clusterapi/serve.go#L47-L49",
        "seb97c68c0964": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/clusterapi/serve.go#L140",
        "saad31a8dae9a": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/cluster/state.go#L695-L705",
        "s8ea0dac76b07": "https://github.com/weaviate/weaviate/blob/v1.39.6/cluster/store.go#L591-L592",
        "sa9c8ff5a4ecc": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L2059-L2061",
        "se2bd8d167284": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/cluster/state.go#L662-L673",
        "s73dc4c7a4cae": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L1804",
        "s09fef29a3bb4": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L822-L823",
        "s59b824177541": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L37-L38",
        "sd40da03c7dea": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L636",
        "sdbd8b8fd06da": "https://github.com/weaviate/weaviate/blob/v1.39.6/cluster/service.go#L152",
        "saed4c2fc8f8f": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L2029",
        "s1ec8942ab969": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L1664",
        "s1a45453a69cc": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/grpc.go#L27-L33",
        "s8e5bf5d887cc": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L86",
        "s839d0ae4019e": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L502-L509",
        "sbd0d3c32cae6": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L733-L736",
        "s8a57e655e250": "https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/config_handler.go#L1333-L1336",
        "s0ba20e752b37": "https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L1736-L1739"
      }
    },
    "wd": {
      "name": "Weaviate documentation",
      "basis": "unknown",
      "sources": {
        "sa066265b9009": "https://docs.weaviate.io/deploy/installation-guides/docker-installation",
        "s51c9c4c6b4c0": "https://docs.weaviate.io/deploy/configuration/authentication",
        "se90546c311e1": "https://docs.weaviate.io/deploy/configuration/env-vars",
        "sb87f55ae205e": "https://docs.weaviate.io/deploy/configuration/authorization",
        "sd5185e505828": "https://docs.weaviate.io/deploy/configuration/configuring-rbac"
      }
    },
    "m2": {
      "name": "Milvus",
      "basis": "v2.6.24",
      "sources": {
        "sd95a54e97bc1": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/base_table.go#L69-L72",
        "s111382ba0af1": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/base_table.go#L145-L153",
        "s53bae912db23": "https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L1036-L1043",
        "se872a9171898": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/grpc_param.go#L112-L139",
        "s978d2f09057a": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/deployments/docker/standalone/docker-compose.yml#L39-L66",
        "s928648b5a0c7": "https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/netutil/listener.go#L11-L35",
        "s53b67fa99640": "https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/interceptor/cluster_interceptor.go#L34-L48",
        "sc4e9500fac07": "https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/utils/util.go#L41-L66",
        "s0d83ff967a6a": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/deployments/docker/standalone/docker-compose.yml#L21-L32",
        "s1b67d9a3bc81": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/service_param.go#L1452-L1477",
        "se914c00355d3": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/server.go#L215-L260",
        "s55fd199759d6": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/server.go#L38-L40",
        "sdf3b1d2a44c0": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/server.go#L77-L120",
        "sb3d4b78cb7bd": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/proxy/management.go#L42-L97",
        "s4443790570be": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/proxy/management.go#L594-L620",
        "s27c6b28106f1": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/restful_mgr_routes.go#L36-L74",
        "s979e91a520e3": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/http_param.go#L71-L78",
        "se193bc422269": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/eventlog/grpc.go#L113-L146",
        "s30534039814b": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/component_param.go#L974-L979",
        "s034ff211eece": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/healthz/healthz_handler.go#L89-L130",
        "sff33760fd71e": "https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L397",
        "se804dabe7939": "https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L623",
        "sd6463e757c5d": "https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L880",
        "sb59cad3a88b8": "https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L309",
        "s2694c200b326": "https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L1322",
        "s21047b546d82": "https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/querynode/service.go#L93-L96",
        "s12f9ee326259": "https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/datanode/service.go#L83-L86",
        "seef04c76c2b8": "https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/streamingnode/service.go#L108-L111",
        "s772289a1421c": "https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/mixcoord/service.go#L99-L102",
        "s6b6cbec16ce7": "https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/proxy/listener_manager.go#L58-L60",
        "s97dca4df88c8": "https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/netutil/listener.go#L92-L103",
        "s3c9efe526b6a": "https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/interceptor/server_id_interceptor.go#L36-L54",
        "s60f9b3f68379": "https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/querynode/service.go#L187-L197",
        "saa07bc24b066": "https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/proto/query_coord.proto#L107-L145",
        "sae3c1aa56572": "https://github.com/milvus-io/milvus/blob/v2.6.24/cmd/milvus/util.go#L143-L148",
        "s3596dd04baa9": "https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L1046",
        "s3b24a2cd0b31": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/distributed/proxy/service.go#L169-L186",
        "se0e67967c9b1": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/rootcoord/root_coord.go#L3180-L3219",
        "s2772deea0984": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/util/hookutil/cipher.go#L390-L401",
        "s34db97d6f273": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/util/hookutil/ez.go#L113-L125",
        "s42ca1740d269": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/mix_coord.go#L237-L240",
        "s2fd8c4230f47": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/metrics/metrics.go#L21",
        "s108ca53f9ce3": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/eventlog/handler.go#L50-L65",
        "s04a87c32f315": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/restful_mgr_routes.go#L881-L890",
        "s597603dbaae3": "https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/restful_mgr_routes.go#L943-L1010"
      }
    },
    "m3": {
      "name": "Milvus",
      "basis": "v3.0.2",
      "sources": {
        "sb8bac089fe22": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/base_table.go#L69-L72",
        "s3631fa007c49": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/base_table.go#L145-L153",
        "s230001e47ba1": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/build/docker/milvus/ubuntu22.04/Dockerfile#L39",
        "s555248062673": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/build/docker/milvus/ubuntu22.04/Dockerfile#L58-L59",
        "sbc585d4a0f5f": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/build/docker/milvus/ubuntu22.04/Dockerfile#L16",
        "s920151033b49": "https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L1155-L1162",
        "s3f8acf8e1aaa": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/grpc_param.go#L111-L138",
        "sdb5a4b72da10": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/deployments/docker/standalone/docker-compose.yml#L39-L66",
        "s6d67ee7d0093": "https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/netutil/listener.go#L11-L35",
        "s0d6581756200": "https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/interceptor/cluster_interceptor.go#L34-L48",
        "s67a44fa31c3b": "https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/utils/util.go#L39-L63",
        "s8b30122d1f5e": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/deployments/docker/standalone/docker-compose.yml#L21-L32",
        "s189b72ec8e6e": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/service_param.go#L1633-L1658",
        "sa564af191a43": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/server.go#L230-L275",
        "s16eac6dca2d2": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/server.go#L37-L39",
        "sc84510615bb1": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/server.go#L82-L127",
        "sb4e87e123555": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L42-L105",
        "sdf2c156e0507": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L427-L447",
        "sf06bcf9fe36d": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L198-L244",
        "s88758dbdf1b1": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L700-L726",
        "s76a0048c7418": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/restful_mgr_routes.go#L33-L71",
        "s0fc696e65913": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/http_param.go#L76-L83",
        "s50ffed832d11": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/eventlog/grpc.go#L113-L146",
        "s4ba2dd6f35d6": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/component_param.go#L1046-L1051",
        "s75885eaffe8b": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/healthz/healthz_handler.go#L87-L128",
        "s4c186d02c419": "https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L458",
        "sab931fc3f694": "https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L690",
        "scd5cdecb245f": "https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L978",
        "s8c703481eb0e": "https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L357",
        "s71ed576f40a9": "https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L1442",
        "s9c1acba22ba3": "https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/querynode/service.go#L123-L126",
        "sfac072fc812f": "https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/datanode/service.go#L82-L85",
        "s05cdfe25ef69": "https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/streamingnode/service.go#L106-L109",
        "s9ffc165c5ec5": "https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/mixcoord/service.go#L97-L100",
        "s1c628a483c2b": "https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/proxy/listener_manager.go#L56-L58",
        "sd4eef5612d16": "https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/netutil/listener.go#L92-L103",
        "s0bd5a9e54516": "https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/interceptor/server_id_interceptor.go#L36-L54",
        "sc65c390b68f2": "https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/querynode/service.go#L243-L253",
        "sb7153655e68f": "https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/proto/query_coord.proto#L109-L147",
        "sdb1c13daa780": "https://github.com/milvus-io/milvus/blob/v3.0.2/cmd/milvus/util.go#L142-L147",
        "s23e57360bafb": "https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L1165",
        "s806e169e81b5": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/distributed/proxy/service.go#L168-L185",
        "s701b77eb1c17": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/rootcoord/root_coord.go#L3464-L3503",
        "sba379e1f515b": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/util/hookutil/cipher.go#L389-L400",
        "s3ad0c01cfa7d": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/util/hookutil/ez.go#L113-L125",
        "s353616d9b3b2": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/mix_coord.go#L242-L245",
        "sc8496db1fb6e": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/metrics/metrics.go#L21",
        "s19e44f8baa1c": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/eventlog/handler.go#L48-L63",
        "s3d76ecf148e0": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/restful_mgr_routes.go#L878-L887",
        "s794c4122f3a1": "https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/restful_mgr_routes.go#L940-L1007"
      }
    },
    "chroma": {
      "name": "Chroma source",
      "basis": "1.5.9",
      "sources": {
        "s7eb7610f68c1": "https://github.com/chroma-core/chroma/blob/1.5.9/rust/cli/src/commands/run.rs#L60-L73",
        "s6d6708278bef": "https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/config.rs#L140-L146",
        "s59912a4c7e11": "https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/sample_configs/docker_single_node.yaml",
        "sed8aad199780": "https://github.com/chroma-core/chroma/blob/1.5.9/rust/cli/src/commands/run.rs#L39-L45",
        "s3a1c76cdd7f8": "https://github.com/chroma-core/chroma/blob/1.5.9/rust/cli/src/commands/run.rs#L114-L134",
        "s09652c32f56a": "https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/config.rs#L176-L179",
        "s784a0e779949": "https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/config.rs#L216-L229"
      }
    },
    "cd": {
      "name": "Chroma migration documentation",
      "basis": "v1.0.0",
      "sources": {
        "s60ad33c4b715": "https://docs.trychroma.com/docs/overview/migration"
      }
    },
    "pg": {
      "name": "pgvector and PostgreSQL documentation",
      "basis": "unknown",
      "sources": {
        "sc5f2c6c39c63": "https://github.com/pgvector/pgvector",
        "se9846041ce1f": "https://www.postgresql.org/docs/current/ddl-rowsecurity.html"
      }
    },
    "docker": {
      "name": "Docker documentation",
      "basis": "unknown",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/",
        "s1dcef979ee57": "https://docs.docker.com/reference/compose-file/services/#env_file",
        "s8f518c10ba0d": "https://docs.docker.com/compose/how-tos/use-secrets/"
      }
    },
    "k8s": {
      "name": "Kubernetes documentation",
      "basis": "unknown",
      "sources": {
        "s953450b4076f": "https://kubernetes.io/docs/concepts/services-networking/network-policies/"
      }
    },
    "grpc2": {
      "name": "grpc-go (Milvus v2.6.24 go.mod)",
      "basis": "v1.82.1",
      "sources": {
        "sa23456a265f8": "https://github.com/grpc/grpc-go/blob/v1.82.1/internal/transport/http2_server.go#L151-L167",
        "s75406e3b5c45": "https://github.com/grpc/grpc-go/blob/v1.82.1/credentials/tls.go#L222-L257",
        "s4e9b30536409": "https://github.com/grpc/grpc-go/blob/v1.82.1/credentials/tls.go#L302-L308"
      }
    },
    "grpc3": {
      "name": "grpc-go (Milvus v3.0.2 go.mod)",
      "basis": "v1.82.2",
      "sources": {
        "sc8c1b3aca796": "https://github.com/grpc/grpc-go/blob/v1.82.2/internal/transport/http2_server.go#L151-L167",
        "sbf5d079c575d": "https://github.com/grpc/grpc-go/blob/v1.82.2/credentials/tls.go#L222-L257",
        "s0fb595ac53b7": "https://github.com/grpc/grpc-go/blob/v1.82.2/credentials/tls.go#L302-L308"
      }
    },
    "ml": {
      "name": "memberlist (Weaviate v1.39.6 go.mod)",
      "basis": "v0.5.4",
      "sources": {
        "s06affccfd439": "https://github.com/hashicorp/memberlist/blob/v0.5.4/config.go#L302-L307",
        "s207b294bb8b4": "https://github.com/hashicorp/memberlist/blob/v0.5.4/net_transport.go#L96-L110",
        "s8b9a9e831368": "https://github.com/hashicorp/memberlist/blob/v0.5.4/net_transport.go#L140-L160"
      }
    },
    "goflags": {
      "name": "go-flags",
      "basis": "v1.6.1",
      "sources": {
        "sbd8f9e746696": "https://github.com/jessevdk/go-flags/blob/v1.6.1/option.go#L328-L343"
      }
    },
    "gostd2": {
      "name": "Go standard library",
      "basis": "go1.25.8",
      "sources": {
        "s2e6578103750": "https://github.com/golang/go/blob/go1.25.8/src/crypto/tls/common.go#L335-L341",
        "s0e02efe6f050": "https://github.com/golang/go/blob/go1.25.8/src/crypto/tls/common.go#L681-L683"
      }
    },
    "gostd3": {
      "name": "Go standard library",
      "basis": "go1.26.6",
      "sources": {
        "s4bd44f1715ab": "https://github.com/golang/go/blob/go1.26.6/src/crypto/tls/common.go#L348-L354",
        "s2809ee3d22bb": "https://github.com/golang/go/blob/go1.26.6/src/crypto/tls/common.go#L698-L700"
      }
    },
    "curl-docs": {
      "name": "curl documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html",
        "s596c6f706038": "https://curl.se/docs/manpage.html#-f"
      }
    }
  },
  "claims": {
    "private-publication": {"text": "Bind privately and publish only a TLS proxy, tunnel or tailnet; Docker loopback mapping avoids default wildcard publication.", "components": ["docker"], "sources": ["docker:s1e53417c513d"], "status": "REASONED"},
    "qdrant-ports": {"text": "Qdrant REST 6333 and gRPC 6334 are client ports; internal gRPC 6335 opens only in distributed mode, including an initial single peer.", "components": ["qd"], "sources": ["qd:s753402e46eed"], "status": "REASONED"},
    "qdrant-bind": {"text": "Compiled host is 0.0.0.0; config/config, RUN_MODE (development default), config/local, deb config, config-path and QDRANT__ variables overlay in that order.", "components": ["q"], "sources": ["q:s7548c65a0e83", "q:sd309f5848ac4"], "status": "REASONED"},
    "qdrant-image": {"text": "Development overlay binds 127.0.0.1; official image sets RUN_MODE=production, keeps 0.0.0.0 and starts qdrant without arguments.", "components": ["q"], "sources": ["q:s6b9ad7f6f7ac", "q:sc0a948c10fcb", "q:s6463d266f693", "q:sfbd6a604b16a"], "status": "REASONED"},
    "qdrant-client-auth": {"text": "Self-deployed Qdrant defaults insecure; api_key and read_only_api_key gate client REST/gRPC through api-key or Bearer headers, with QDRANT__SERVICE__ environment equivalents.", "components": ["qd"], "sources": ["qd:s753402e46eed"], "status": "REASONED"},
    "qdrant-client-tls": {"text": "service.enable_tls with tls.cert/key enables client TLS; keys without TLS are insecure.", "components": ["qd"], "sources": ["qd:s753402e46eed"], "status": "REASONED"},
    "qdrant-peer-auth": {"text": "Through v1.17.x keys do not gate 6335; v1.18.0 adds enforce_internal_auth, off by default and deferred through rolling upgrades; retain peer-only network restriction.", "components": ["qd"], "sources": ["qd:s753402e46eed"], "status": "REASONED"},
    "qdrant-peer-tls": {"text": "cluster.p2p.enable_tls is separate from client TLS and needs a provisioned tls.ca_cert; compiled default path is not a substitute for provisioning.", "components": ["qd"], "sources": ["qd:s753402e46eed"], "status": "REASONED"},
    "qdrant-rotation": {"text": "alt_api_key accepts an additional client key from v1.17.0; rotate peer-by-peer, with internal use only under enforce_internal_auth from v1.18.0.", "components": ["qd"], "sources": ["qd:s753402e46eed"], "status": "REASONED"},
    "weaviate-precedence": {"text": "File, environment then flags override settings; environment reapplies gRPC/Raft port defaults when unset/empty and gossip/API defaults when unset; empty cluster port variables fail startup.", "components": ["w"], "sources": ["w:s8c45722d725f", "w:sb916723717de", "w:s7c30e1e2c554", "w:s85b7b3e8fa18", "w:s8c05965785ea", "w:sbd0d3c32cae6", "w:s8a57e655e250", "w:s0ba20e752b37"], "status": "REASONED"},
    "weaviate-rest": {"text": "Default scheme is HTTPS requiring certificates or startup fails; TLS host falls back to host and TLS port is random. HTTP host defaults localhost unless HOST is exported empty; port defaults random; unix uses socket-path.", "components": ["w", "goflags"], "sources": ["w:sa1cbcde2f024", "w:s122708a42282", "w:s5b7738072d06", "w:s71035079ef45", "w:s7b8a55a31a45", "w:sc6fc7e030ce0", "w:s8e5bf5d887cc", "goflags:sbd8f9e746696"], "status": "REASONED"},
    "weaviate-image": {"text": "Official image selects HTTP on 0.0.0.0:8080; documented proxy forwards both 8080 and gRPC 50051 with TLS at the proxy.", "components": ["w", "wd"], "sources": ["w:se5771dfe00cc", "wd:sa066265b9009"], "status": "REASONED"},
    "weaviate-grpc": {"text": "gRPC always starts on a wildcard address with default port 50051 (configurable via GRPC_PORT) and ignores REST host; keep it unpublished except through the intended proxy.", "components": ["w"], "sources": ["w:s4d2b119da409", "w:s85b7b3e8fa18", "w:saed4c2fc8f8f", "w:s1ec8942ab969", "w:s1a45453a69cc"], "status": "REASONED"},
    "weaviate-debug": {"text": "Debug HTTP defaults wildcard 6060 unless GO_PROFILING_DISABLE is true; debug endpoints return 404 until enabled.", "components": ["w"], "sources": ["w:sd53f51213b12", "w:sae4bd165c1f1", "w:sc1473599ecd1", "w:s839d0ae4019e"], "status": "REASONED"},
    "weaviate-metrics": {"text": "Enabled Prometheus listener exposes metrics and tenant-activity on wildcard, default 2112 when enabled through environment; admit only scraper traffic.", "components": ["w"], "sources": ["w:s909e461943ae", "w:s3d7fe59cb2c4"], "status": "REASONED"},
    "weaviate-gossip": {"text": "Even one node opens TCP/UDP gossip 7946 at CLUSTER_BIND_ADDR, defaulting to wildcard when unset/empty; admit only peers.", "components": ["w", "ml"], "sources": ["w:s8c05965785ea", "w:saad31a8dae9a", "w:sa9c8ff5a4ecc", "w:se2bd8d167284", "w:s73dc4c7a4cae", "ml:s06affccfd439", "ml:s207b294bb8b4"], "status": "REASONED"},
    "weaviate-cluster-api": {"text": "Internal cluster API binds wildcard 7947, default gossip port plus one, independently of REST host.", "components": ["w"], "sources": ["w:sc8c8851851c6", "w:seb97c68c0964", "w:s8c05965785ea", "w:sa9c8ff5a4ecc", "w:s09fef29a3bb4"], "status": "REASONED"},
    "weaviate-raft": {"text": "Raft 8300 and RPC 8301 bind nonempty CLUSTER_BIND_ADDR, then CLUSTER_ADVERTISE_ADDR, then memberlist private advertise address; keep peer-only.", "components": ["w", "ml"], "sources": ["w:s8c05965785ea", "w:s8ea0dac76b07", "w:s8c15def0d8e9", "w:s59b824177541", "w:sd40da03c7dea", "w:sdbd8b8fd06da", "ml:s8b9a9e831368"], "status": "REASONED"},
    "weaviate-auth": {"text": "Anonymous access defaults true; disable it and enable API keys with positional key-to-user mapping.", "components": ["wd"], "sources": ["wd:s51c9c4c6b4c0", "wd:se90546c311e1"], "status": "REASONED"},
    "weaviate-rbac": {"text": "Enable RBAC, root only the admin, and scope app roles to collections; RBAC is stated generally available from v1.29 and cannot combine with admin-list authorization.", "components": ["wd"], "sources": ["wd:sb87f55ae205e", "wd:sd5185e505828"], "status": "REASONED"},
    "weaviate-oidc": {"text": "OIDC issuer/client settings delegate human authentication and MFA to the IdP; authentication alone is not authorization.", "components": ["wd"], "sources": ["wd:s51c9c4c6b4c0"], "status": "REASONED"},
    "milvus-config": {"text": "Compose mounts only data; mount user.yaml and TLS files read-only under /milvus, accounting for MILVUSCONF and milvus.yaml/_test.yaml/default.yaml/user.yaml precedence.", "components": ["m2", "m3"], "sources": ["m2:sd95a54e97bc1", "m3:sb8bac089fe22"], "status": "REASONED"},
    "milvus-env": {"text": "Environment formatter lowercases, strips leading milvus. and removes slash/underscore/dot; use COMMON_SECURITY_* and TLS_* names, remove conflicting sources and recreate changed mounts/environment.", "components": ["m2", "m3"], "sources": ["m2:s111382ba0af1", "m3:s3631fa007c49"], "status": "REASONED"},
    "milvus-user": {"text": "v3.0.2 Ubuntu image runs as milvus; make config/certificates readable and restrict the private key to the service and trusted administrators.", "components": ["m3"], "sources": ["m3:s230001e47ba1", "m3:s555248062673", "m3:sbc585d4a0f5f"], "status": "REASONED"},
    "milvus-auth": {"text": "Enable common.security.authorizationEnabled, replace built-in root/Milvus and create a per-app user; proxy auth does not protect internal services.", "components": ["m2", "m3"], "sources": ["m2:s53bae912db23", "m3:s920151033b49"], "status": "REASONED"},
    "milvus-tls": {"text": "tls server/key/CA paths and common.security.tlsMode 1 enable server TLS; mode 2 requires client certificates; enable authentication independently.", "components": ["m2", "m3"], "sources": ["m2:se872a9171898", "m3:s3f8acf8e1aaa"], "status": "REASONED"},
    "milvus-client": {"text": "External client gRPC uses 19530; publish only that port privately, apart from the optional loopback management mapping.", "components": ["m2", "m3"], "sources": ["m2:s978d2f09057a", "m3:sdb5a4b72da10"], "status": "REASONED"},
    "milvus-internal": {"text": "Internal proxy 19529, query 21123, data 21124, mix coordinator 22125 and streaming 22222 bind wildcard; node ports can fall back randomly and advertised ip is not a bind.", "components": ["m2", "m3"], "sources": ["m2:s928648b5a0c7", "m3:s6d67ee7d0093", "m2:sff33760fd71e", "m2:se804dabe7939", "m2:sd6463e757c5d", "m2:sb59cad3a88b8", "m2:s2694c200b326", "m2:s21047b546d82", "m2:s12f9ee326259", "m2:seef04c76c2b8", "m2:s772289a1421c", "m2:s6b6cbec16ce7", "m2:s97dca4df88c8", "m3:s4c186d02c419", "m3:sab931fc3f694", "m3:scd5cdecb245f", "m3:s8c703481eb0e", "m3:s71ed576f40a9", "m3:s9c1acba22ba3", "m3:sfac072fc812f", "m3:s05cdfe25ef69", "m3:s9ffc165c5ec5", "m3:s1c628a483c2b", "m3:sd4eef5612d16"], "status": "REASONED"},
    "milvus-internal-auth": {"text": "Internal routing interceptors pass calls without metadata and do not authenticate Search/Query; standalone runs all five components.", "components": ["m2", "m3"], "sources": ["m2:s53b67fa99640", "m3:s0d6581756200", "m2:s3c9efe526b6a", "m2:s60f9b3f68379", "m2:saa07bc24b066", "m2:sae3c1aa56572", "m3:s0bd5a9e54516", "m3:sc65c390b68f2", "m3:sb7153655e68f", "m3:sdb1c13daa780"], "status": "REASONED"},
    "milvus-internal-tls": {"text": "internaltlsEnabled defaults off; internal TLS is one-way and failed certificate/key loading logs a warning then serves plaintext.", "components": ["m2", "m3", "grpc2", "grpc3", "gostd2", "gostd3"], "sources": ["m2:sc4e9500fac07", "m3:s67a44fa31c3b", "m2:s3596dd04baa9", "m3:s23e57360bafb", "grpc2:sa23456a265f8", "grpc3:sc8c1b3aca796", "grpc2:s4e9b30536409", "grpc3:s0fb595ac53b7", "grpc2:s75406e3b5c45", "grpc3:sbf5d079c575d", "gostd2:s2e6578103750", "gostd2:s0e02efe6f050", "gostd3:s4bd44f1715ab", "gostd3:s2809ee3d22bb"], "status": "REASONED"},
    "milvus-isolation": {"text": "Use a dedicated network, no host/shared namespace, and default-deny rules admitting peers by source including random fallback ports; exclude untrusted workloads/users from component hosts.", "components": ["docker", "k8s"], "sources": ["docker:s1e53417c513d", "k8s:s953450b4076f"], "status": "REASONED"},
    "milvus-minio-ports": {"text": "Bundled MinIO publishes wildcard 9000 API and 9001 console while etcd remains internal; restrict both and replace default credentials.", "components": ["m2", "m3"], "sources": ["m2:s0d83ff967a6a", "m3:s8b30122d1f5e"], "status": "REASONED"},
    "milvus-storage-credentials": {"text": "Pinned Compose selects MinIO RELEASE.2024-05-28T17-19-04Z with MINIO_ACCESS_KEY/SECRET_KEY=minioadmin; Milvus uses MINIO_ACCESS_KEY_ID/SECRET_ACCESS_KEY; rotate matching pairs together.", "components": ["m2", "m3"], "sources": ["m2:s1b67d9a3bc81", "m3:s189b72ec8e6e"], "status": "REASONED"},
    "milvus-env-files": {"text": "Use protected untracked env-files, delete overriding Compose environment credential entries, retain ETCD_ENDPOINTS/MINIO_ADDRESS/MINIO_REGION and recreate both services; container environment remains inspectable.", "components": ["docker"], "sources": ["docker:s1dcef979ee57", "docker:s8f518c10ba0d"], "status": "REASONED"},
    "milvus-compose-images": {"text": "Compose at v2.6.24 and v3.0.2 selects older Milvus images v2.6.23 and v3.0.1; explicitly choose and recheck the intended image.", "components": ["m2", "m3"], "sources": ["m2:s978d2f09057a", "m3:sdb5a4b72da10"], "status": "REASONED"},
    "milvus-management": {"text": "Management HTTP defaults wildcard 9091 with no bind-address control; METRICS_PORT parse failures fall back, 0 chooses random and other out-of-range values fail listen without stopping Milvus.", "components": ["m2", "m3"], "sources": ["m2:se914c00355d3", "m2:s55fd199759d6", "m2:sdf3b1d2a44c0", "m3:sa564af191a43", "m3:s16eac6dca2d2", "m3:sc84510615bb1"], "status": "REASONED"},
    "milvus-control": {"text": "Management routes bypass proxy authorization: log-level changes, process-role stop, GC/balancing/node controls and transfers remain exposed even with WebUI disabled.", "components": ["m2", "m3"], "sources": ["m2:sb3d4b78cb7bd", "m3:sb4e87e123555", "m2:sdf3b1d2a44c0", "m2:se914c00355d3", "m2:s3b24a2cd0b31", "m3:sc84510615bb1", "m3:sa564af191a43", "m3:s806e169e81b5"], "status": "REASONED"},
    "milvus-key-backup": {"text": "Management encryption-zone backup returns the plugin backup for eligible databases; v3.0.2 also adds queued-read clearing and path-supplied backfill commit.", "components": ["m2", "m3"], "sources": ["m2:sb3d4b78cb7bd", "m2:s4443790570be", "m3:sf06bcf9fe36d", "m3:sb4e87e123555", "m3:sdf2c156e0507", "m3:s88758dbdf1b1", "m2:se0e67967c9b1", "m2:s2772deea0984", "m2:s34db97d6f273", "m3:s701b77eb1c17", "m3:sba379e1f515b", "m3:s3ad0c01cfa7d"], "status": "REASONED"},
    "milvus-coordinator": {"text": "Activated mix coordinator adds mutable configuration and WAL changes alongside GC, balancing, suspension and transfer controls.", "components": ["m2", "m3"], "sources": ["m2:s27c6b28106f1", "m3:s76a0048c7418", "m2:s42ca1740d269", "m3:s353616d9b3b2", "m2:s04a87c32f315", "m2:s597603dbaae3", "m3:s3d76ecf148e0", "m3:s794c4122f3a1"], "status": "REASONED"},
    "milvus-profiling": {"text": "proxy.http.enablePprof defaults true; disabling profiling omits pprof but leaves control routes registered.", "components": ["m2", "m3"], "sources": ["m2:s979e91a520e3", "m3:s0fc696e65913", "m2:se914c00355d3", "m2:s2fd8c4230f47", "m3:sa564af191a43", "m3:sc8496db1fb6e"], "status": "REASONED"},
    "milvus-eventlog": {"text": "First successful eventlog request opens an unauthenticated, non-TLS wildcard gRPC listener on a random port; repeat inventory after requests.", "components": ["m2", "m3"], "sources": ["m2:se193bc422269", "m3:s50ffed832d11", "m2:s108ca53f9ce3", "m3:s19e44f8baa1c"], "status": "REASONED"},
    "milvus-health": {"text": "Delete wildcard 9091 publication; in-container healthcheck needs none. Optional 127.0.0.1:9091 mapping still needs isolation; changed METRICS_PORT must update healthcheck and mappings.", "components": ["m2", "m3"], "sources": ["m2:s978d2f09057a", "m3:sdb5a4b72da10"], "status": "REASONED"},
    "chroma-bind": {"text": "Without a file chroma run defaults localhost; a config file defaults listen_address to 0.0.0.0 after CHROMA_ merges; official config sets only persist_path, yielding wildcard 8000.", "components": ["chroma"], "sources": ["chroma:s7eb7610f68c1", "chroma:s6d6708278bef", "chroma:s59912a4c7e11", "chroma:sed8aad199780", "chroma:s3a1c76cdd7f8", "chroma:s09652c32f56a", "chroma:s784a0e779949"], "status": "REASONED"},
    "chroma-auth": {"text": "Built-in authentication was removed in v1.0.0; obsolete AUTHN variables do not protect the server. Use private binding and authenticated TLS fronting.", "components": ["cd"], "sources": ["cd:s60ad33c4b715"], "status": "REASONED"},
    "pgvector": {"text": "pgvector is a PostgreSQL extension on 5432 for PostgreSQL 13+; use PostgreSQL TLS, hostssl/SCRAM, verify-full and least-privilege roles.", "components": ["pg"], "sources": ["pg:sc5f2c6c39c63"], "status": "REASONED"},
    "pgvector-rls": {"text": "Tenant RLS filters shared embeddings; prove tenant-B isolation with known rows and bypass controls, counting per tenant rather than trusting top-k.", "components": ["pg"], "sources": ["pg:se9846041ce1f"], "status": "REASONED"},
    "hosted-mfa": {"text": "Hosted keys stay secret and clients use vendor HTTPS; human MFA belongs on hosted consoles, Weaviate OIDC or the fronting layer, not a self-hosted API key.", "components": ["qd", "wd"], "sources": ["qd:s753402e46eed", "wd:s51c9c4c6b4c0"], "status": "REASONED"},
    "verify-inventory": {"text": "Read all listener rows, container namespaces and publications; expected-port grep and host ss alone can miss exposure.", "components": ["qd", "docker"], "sources": ["qd:s753402e46eed", "docker:s1e53417c513d"], "status": "REASONED", "verify": [1]},
    "verify-peer": {"text": "Probe real backend 6333/6334/6335 from non-peers; require connection failure with filtering evidence and a positive peer control for 6335; auth/TLS rejection is still reachability.", "components": ["qd", "curl-docs"], "sources": ["qd:s753402e46eed", "curl-docs:s2b2686afaf41", "curl-docs:s596c6f706038"], "status": "REASONED", "verify": [2]},
    "verify-curl": {"text": "exit 3/6 is invalid input; 7 or a five-second 28 needs corroboration; nonzero HTTP, 52/56 or a twenty-second 28 indicates reachability, including HTTP 000 cases.", "components": ["curl-docs"], "sources": ["curl-docs:s2b2686afaf41", "curl-docs:s596c6f706038"], "status": "REASONED", "verify": [2]},
    "verify-qdrant-auth": {"text": "Frontend collections check expects anonymous 401/403 and keyed 200 over verified TLS; both can pass while peer port 6335 is exposed.", "components": ["qd"], "sources": ["qd:s753402e46eed"], "status": "REASONED", "verify": [3]},
    "verify-fronting": {"text": "Weaviate schema rejects anonymous access and allows a valid key; Chroma requires fronting denial and authorized success because it has no native auth.", "components": ["wd", "cd"], "sources": ["wd:s51c9c4c6b4c0", "cd:s60ad33c4b715"], "status": "REASONED", "verify": [4]},
    "verify-milvus-auth": {"text": "MilvusClient without a token must fail after authorization is enabled, while the same operation with the application identity succeeds.", "components": ["m2", "m3"], "sources": ["m2:s30534039814b", "m3:s4ba2dd6f35d6"], "status": "REASONED"},
    "verify-milvus-management": {"text": "Outside-admin reachability fails; private control needs healthy Compose status and the milvus-owned listener, since healthz can pass before registration and bind failure is nonfatal.", "components": ["m2", "m3"], "sources": ["m2:s034ff211eece", "m3:s75885eaffe8b", "m2:se914c00355d3", "m3:sa564af191a43"], "status": "REASONED", "verify": [1, 2]}
  }
}
---
# Vector databases: Qdrant, Weaviate, Milvus, Chroma, pgvector

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| private-publication: Bind privately and publish only a TLS proxy, tunnel or tailnet; Docker loopback mapping avoids default wildcard publication. | Docker documentation unknown | REASONED |
| qdrant-ports: Qdrant REST 6333 and gRPC 6334 are client ports; internal gRPC 6335 opens only in distributed mode, including an initial single peer. | Qdrant security documentation unknown | REASONED |
| qdrant-bind: Compiled host is 0.0.0.0; config/config, RUN_MODE (development default), config/local, deb config, config-path and QDRANT__ variables overlay in that order. | Qdrant source v1.19.1 | REASONED |
| qdrant-image: Development overlay binds 127.0.0.1; official image sets RUN_MODE=production, keeps 0.0.0.0 and starts qdrant without arguments. | Qdrant source v1.19.1 | REASONED |
| qdrant-client-auth: Self-deployed Qdrant defaults insecure; api_key and read_only_api_key gate client REST/gRPC through api-key or Bearer headers, with QDRANT__SERVICE__ environment equivalents. | Qdrant security documentation unknown | REASONED |
| qdrant-client-tls: service.enable_tls with tls.cert/key enables client TLS; keys without TLS are insecure. | Qdrant security documentation unknown | REASONED |
| qdrant-peer-auth: Through v1.17.x keys do not gate 6335; v1.18.0 adds enforce_internal_auth, off by default and deferred through rolling upgrades; retain peer-only network restriction. | Qdrant security documentation unknown | REASONED |
| qdrant-peer-tls: cluster.p2p.enable_tls is separate from client TLS and needs a provisioned tls.ca_cert; compiled default path is not a substitute for provisioning. | Qdrant security documentation unknown | REASONED |
| qdrant-rotation: alt_api_key accepts an additional client key from v1.17.0; rotate peer-by-peer, with internal use only under enforce_internal_auth from v1.18.0. | Qdrant security documentation unknown | REASONED |
| weaviate-precedence: File, environment then flags override settings; environment reapplies gRPC/Raft port defaults when unset/empty and gossip/API defaults when unset; empty cluster port variables fail startup. | Weaviate source v1.39.6 | REASONED |
| weaviate-rest: Default scheme is HTTPS requiring certificates or startup fails; TLS host falls back to host and TLS port is random. HTTP host defaults localhost unless HOST is exported empty; port defaults random; unix uses socket-path. | Weaviate source v1.39.6; go-flags v1.6.1 | REASONED |
| weaviate-image: Official image selects HTTP on 0.0.0.0:8080; documented proxy forwards both 8080 and gRPC 50051 with TLS at the proxy. | Weaviate source v1.39.6; Weaviate documentation unknown | REASONED |
| weaviate-grpc: gRPC always starts on a wildcard address with default port 50051 (configurable via GRPC_PORT) and ignores REST host; keep it unpublished except through the intended proxy. | Weaviate source v1.39.6 | REASONED |
| weaviate-debug: Debug HTTP defaults wildcard 6060 unless GO_PROFILING_DISABLE is true; debug endpoints return 404 until enabled. | Weaviate source v1.39.6 | REASONED |
| weaviate-metrics: Enabled Prometheus listener exposes metrics and tenant-activity on wildcard, default 2112 when enabled through environment; admit only scraper traffic. | Weaviate source v1.39.6 | REASONED |
| weaviate-gossip: Even one node opens TCP/UDP gossip 7946 at CLUSTER_BIND_ADDR, defaulting to wildcard when unset/empty; admit only peers. | Weaviate source v1.39.6; memberlist (Weaviate v1.39.6 go.mod) v0.5.4 | REASONED |
| weaviate-cluster-api: Internal cluster API binds wildcard 7947, default gossip port plus one, independently of REST host. | Weaviate source v1.39.6 | REASONED |
| weaviate-raft: Raft 8300 and RPC 8301 bind nonempty CLUSTER_BIND_ADDR, then CLUSTER_ADVERTISE_ADDR, then memberlist private advertise address; keep peer-only. | Weaviate source v1.39.6; memberlist (Weaviate v1.39.6 go.mod) v0.5.4 | REASONED |
| weaviate-auth: Anonymous access defaults true; disable it and enable API keys with positional key-to-user mapping. | Weaviate documentation unknown | REASONED |
| weaviate-rbac: Enable RBAC, root only the admin, and scope app roles to collections; RBAC is stated generally available from v1.29 and cannot combine with admin-list authorization. | Weaviate documentation unknown | REASONED |
| weaviate-oidc: OIDC issuer/client settings delegate human authentication and MFA to the IdP; authentication alone is not authorization. | Weaviate documentation unknown | REASONED |
| milvus-config: Compose mounts only data; mount user.yaml and TLS files read-only under /milvus, accounting for MILVUSCONF and milvus.yaml/_test.yaml/default.yaml/user.yaml precedence. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-env: Environment formatter lowercases, strips leading milvus. and removes slash/underscore/dot; use COMMON_SECURITY_* and TLS_* names, remove conflicting sources and recreate changed mounts/environment. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-user: v3.0.2 Ubuntu image runs as milvus; make config/certificates readable and restrict the private key to the service and trusted administrators. | Milvus v3.0.2 | REASONED |
| milvus-auth: Enable common.security.authorizationEnabled, replace built-in root/Milvus and create a per-app user; proxy auth does not protect internal services. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-tls: tls server/key/CA paths and common.security.tlsMode 1 enable server TLS; mode 2 requires client certificates; enable authentication independently. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-client: External client gRPC uses 19530; publish only that port privately, apart from the optional loopback management mapping. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-internal: Internal proxy 19529, query 21123, data 21124, mix coordinator 22125 and streaming 22222 bind wildcard; node ports can fall back randomly and advertised ip is not a bind. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-internal-auth: Internal routing interceptors pass calls without metadata and do not authenticate Search/Query; standalone runs all five components. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-internal-tls: internaltlsEnabled defaults off; internal TLS is one-way and failed certificate/key loading logs a warning then serves plaintext. | Milvus v2.6.24; Milvus v3.0.2; grpc-go (Milvus v2.6.24 go.mod) v1.82.1; grpc-go (Milvus v3.0.2 go.mod) v1.82.2; Go standard library go1.25.8; Go standard library go1.26.6 | REASONED |
| milvus-isolation: Use a dedicated network, no host/shared namespace, and default-deny rules admitting peers by source including random fallback ports; exclude untrusted workloads/users from component hosts. | Docker documentation unknown; Kubernetes documentation unknown | REASONED |
| milvus-minio-ports: Bundled MinIO publishes wildcard 9000 API and 9001 console while etcd remains internal; restrict both and replace default credentials. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-storage-credentials: Pinned Compose selects MinIO RELEASE.2024-05-28T17-19-04Z with MINIO_ACCESS_KEY/SECRET_KEY=minioadmin; Milvus uses MINIO_ACCESS_KEY_ID/SECRET_ACCESS_KEY; rotate matching pairs together. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-env-files: Use protected untracked env-files, delete overriding Compose environment credential entries, retain ETCD_ENDPOINTS/MINIO_ADDRESS/MINIO_REGION and recreate both services; container environment remains inspectable. | Docker documentation unknown | REASONED |
| milvus-compose-images: Compose at v2.6.24 and v3.0.2 selects older Milvus images v2.6.23 and v3.0.1; explicitly choose and recheck the intended image. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-management: Management HTTP defaults wildcard 9091 with no bind-address control; METRICS_PORT parse failures fall back, 0 chooses random and other out-of-range values fail listen without stopping Milvus. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-control: Management routes bypass proxy authorization: log-level changes, process-role stop, GC/balancing/node controls and transfers remain exposed even with WebUI disabled. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-key-backup: Management encryption-zone backup returns the plugin backup for eligible databases; v3.0.2 also adds queued-read clearing and path-supplied backfill commit. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-coordinator: Activated mix coordinator adds mutable configuration and WAL changes alongside GC, balancing, suspension and transfer controls. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-profiling: proxy.http.enablePprof defaults true; disabling profiling omits pprof but leaves control routes registered. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-eventlog: First successful eventlog request opens an unauthenticated, non-TLS wildcard gRPC listener on a random port; repeat inventory after requests. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| milvus-health: Delete wildcard 9091 publication; in-container healthcheck needs none. Optional 127.0.0.1:9091 mapping still needs isolation; changed METRICS_PORT must update healthcheck and mappings. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| chroma-bind: Without a file chroma run defaults localhost; a config file defaults listen_address to 0.0.0.0 after CHROMA_ merges; official config sets only persist_path, yielding wildcard 8000. | Chroma source 1.5.9 | REASONED |
| chroma-auth: Built-in authentication was removed in v1.0.0; obsolete AUTHN variables do not protect the server. Use private binding and authenticated TLS fronting. | Chroma migration documentation v1.0.0 | REASONED |
| pgvector: pgvector is a PostgreSQL extension on 5432 for PostgreSQL 13+; use PostgreSQL TLS, hostssl/SCRAM, verify-full and least-privilege roles. | pgvector and PostgreSQL documentation unknown | REASONED |
| pgvector-rls: Tenant RLS filters shared embeddings; prove tenant-B isolation with known rows and bypass controls, counting per tenant rather than trusting top-k. | pgvector and PostgreSQL documentation unknown | REASONED |
| hosted-mfa: Hosted keys stay secret and clients use vendor HTTPS; human MFA belongs on hosted consoles, Weaviate OIDC or the fronting layer, not a self-hosted API key. | Qdrant security documentation unknown; Weaviate documentation unknown | REASONED |
| verify-inventory: Read all listener rows, container namespaces and publications; expected-port grep and host ss alone can miss exposure. | Qdrant security documentation unknown; Docker documentation unknown | REASONED |
| verify-peer: Probe real backend 6333/6334/6335 from non-peers; require connection failure with filtering evidence and a positive peer control for 6335; auth/TLS rejection is still reachability. | Qdrant security documentation unknown; curl documentation (rolling) unknown | REASONED |
| verify-curl: exit 3/6 is invalid input; 7 or a five-second 28 needs corroboration; nonzero HTTP, 52/56 or a twenty-second 28 indicates reachability, including HTTP 000 cases. | curl documentation (rolling) unknown | REASONED |
| verify-qdrant-auth: Frontend collections check expects anonymous 401/403 and keyed 200 over verified TLS; both can pass while peer port 6335 is exposed. | Qdrant security documentation unknown | REASONED |
| verify-fronting: Weaviate schema rejects anonymous access and allows a valid key; Chroma requires fronting denial and authorized success because it has no native auth. | Weaviate documentation unknown; Chroma migration documentation v1.0.0 | REASONED |
| verify-milvus-auth: MilvusClient without a token must fail after authorization is enabled, while the same operation with the application identity succeeds. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
| verify-milvus-management: Outside-admin reachability fails; private control needs healthy Compose status and the milvus-owned listener, since healthz can pass before registration and bind failure is nonfatal. | Milvus v2.6.24; Milvus v3.0.2 | REASONED |
<!-- version-basis:end -->

A RAG store holds every document the application was given, often including private data, and it answers similarity queries that reconstruct that text. Several of these servers ship with no authentication enabled and none of them serves TLS out of the box, so an exposed default install is a searchable copy of your corpus. Keep the store on a private interface, turn on the native key or account control where one exists, and put TLS in front or on the server before any client crosses a network.

## 1. Bind privately

Each server listens on plain TCP; publish only a reverse proxy ([nginx.md](nginx.md), [caddy.md](caddy.md)), a tunnel ([cloudflare.md](cloudflare.md)), or a tailnet ([tailscale.md](tailscale.md)). In Docker, map to loopback (`-p 127.0.0.1:6333:6333`), not `-p 6333:6333`, which binds every interface ([docker.md](docker.md)). Default ports, from the vendor pages in Sources:

| Server | Default ports |
|---|---|
| Qdrant | 6333 (REST), 6334 (gRPC), 6335 (internal cluster gRPC, distributed mode only) |
| Weaviate | 8080 (HTTP), 50051 (gRPC) |
| Milvus | 19530 (gRPC), 9091 (management/metrics HTTP, optional WebUI); internal: 19529, 21123, 21124, 22125, 22222 |
| Chroma | 8000 |
| pgvector | 5432 (it is PostgreSQL) |

Qdrant and Chroma bind every IPv4 interface by default in their official images, and Weaviate opens several listeners that ignore `--host` wherever it runs (as of Qdrant v1.19.1, Chroma 1.5.9 and Weaviate v1.39.6):

- **Qdrant**'s compiled-in configuration sets `service.host: 0.0.0.0`. It then merges `config/config`, `config/$RUN_MODE` (`RUN_MODE` defaults to `development`) and `config/local` from the working directory, then, in a build with the `deb` feature, `/etc/qdrant/config`, then `--config-path`, then `QDRANT__`-prefixed environment variables; any later layer can set the host. The repository's `config/development.yaml` narrows it to `127.0.0.1`, so a binary started from a checkout's root with `RUN_MODE` unset or `development` listens on loopback unless a later layer sets it; the official image sets `RUN_MODE=production`, whose `config/production.yaml` keeps `0.0.0.0`, and its entrypoint starts `./qdrant` with no arguments.
- **Chroma**'s `chroma run` without a config file binds `localhost`, its `--host` default. Given a config file, it binds the file's `listen_address`, or `0.0.0.0` when the file sets none, after merging `CHROMA_`-prefixed environment variables. The official `chromadb/chroma` image runs `chroma run /config.yaml` with a file that sets only `persist_path`, so the container listens on `0.0.0.0:8000` unless a `CHROMA_`-prefixed variable sets the address or port.
- **Weaviate** reads most settings from a config file (`--config-file`), then environment variables, then command-line flags, each overriding the one before. Every port below, and every address that has a setting, is a default, but the environment step re-applies the default for the gRPC and Raft ports whenever their variable is unset or empty, and for the gossip and cluster-API ports whenever theirs is unset (an empty `CLUSTER_GOSSIP_BIND_PORT` or `CLUSTER_DATA_BIND_PORT` stops startup with a parse error), so a port set only in the config file does not take effect for those; set ports through their variables (or, for REST and Raft, flags) and confirm with `ss`. The gRPC, debug, Prometheus and cluster-API listeners have no address setting and bind every local address whenever they run. Its REST listener depends on `--scheme`. Without it, the API spec's default is `https`, which needs a certificate and key (`--tls-certificate` and `--tls-key`, or `TLS_CERTIFICATE` and `TLS_PRIVATE_KEY`) or Weaviate exits at startup; with them it binds `--tls-host` (`TLS_HOST`, falling back to `--host`) on a random `--tls-port`. With `--scheme http`, as the official `semitechnologies/weaviate` image passes (with `--host 0.0.0.0 --port 8080`), it binds `--host` (`HOST`; the default `localhost` applies only while `HOST` is unset, since an exported but empty `HOST` binds every local address) on `--port` (random by default); `unix` binds `--socket-path`. None of Weaviate's other listeners follows `--host`: gRPC always starts, on every local address, on 50051 unless `GRPC_PORT` sets another port; the debug HTTP listener (pprof and fgprof) binds 6060 on every local address unless `GO_PROFILING_DISABLE` is set to a true value, and answers 404 until debug endpoints are enabled; the Prometheus listener (`/metrics` and `/tenant-activity`) binds every local address when monitoring is enabled, on 2112 when `PROMETHEUS_MONITORING_ENABLED` enables it; and even a single node opens memberlist gossip on 7946 (TCP and UDP) at `CLUSTER_BIND_ADDR`, or on every local address (`0.0.0.0`) when that is unset or empty, the internal cluster API on 7947 (the gossip port plus one by default) on every local address, and Raft on 8300 with its internal RPC on 8301 at a non-empty `CLUSTER_BIND_ADDR`, else a non-empty `CLUSTER_ADVERTISE_ADDR`, else the private address memberlist advertises. Keep 50051, 6060, 2112, 7946, 7947, 8300 and 8301 unpublished, opening the cluster ports only to peers and 2112 only to the metrics scraper.

## 2. Qdrant: API key and TLS

Per the Qdrant security page, "all self-deployed Qdrant instances are not secure" by default and connections are unencrypted. Set an API key in the config file or through the environment, and add a read-only key for query-only clients:

```yaml
service:
  api_key: REPLACE_WITH_LONG_RANDOM_VALUE
  read_only_api_key: REPLACE_WITH_ANOTHER_LONG_RANDOM_VALUE
  enable_tls: true

tls:
  cert: ./tls/cert.pem
  key: ./tls/key.pem
```

Environment equivalents: `QDRANT__SERVICE__API_KEY` and `QDRANT__SERVICE__READ_ONLY_API_KEY`. Clients send the key in the `api-key` header (or `Authorization: Bearer`); the two are interchangeable for the client REST and gRPC API. Qdrant's own docs say that enabling the key without TLS is insecure; terminate TLS either in Qdrant as above or at a proxy in front.

An API key protects the client API. It does not protect the internal cluster port, 6335. The security page states, exactly: "Internal communication channels are *never* protected by an API key nor bearer tokens. Internal gRPC uses port 6335 by default if running in distributed mode. You must ensure that this port is not publicly reachable and can only be used for node communication." Through v1.17.x this is not a gap a key can close. Qdrant v1.18.0 added `service.enforce_internal_auth`: with it set, the receiving peer verifies the forwarded `api_key` on internal p2p requests, so a key can gate 6335 on v1.18.0 and later. It is off by default, and the vendor recommends leaving it off through a rolling upgrade until every node is on the new version, so do not rely on it in place of the network restriction below. `read_only_api_key` does not cover 6335 either, and confirming that 6333 returns 401 without a key tells you nothing about 6335: in distributed mode 6335 answers a peer with no API key or bearer token (peer TLS, when enabled, authenticates the channel by certificate; a key applies to the internal channel only where `enforce_internal_auth` is set, on v1.18.0 and later), so a reader who sets a key, sees 6333 return 401, and concludes the deployment is authenticated is wrong about 6335.

Restrict 6335 to your cluster peers at the network layer, with a host firewall, a cloud security group, or by simply not publishing the container port to any address a non-peer can reach. Allow inbound 6335 only from your other peers' addresses and deny every other source, including other machines on the same private network. A node not running in cluster mode does not open 6335 at all; note that a single initial node started WITH cluster mode enabled does open the internal listener, so "single host" is not by itself a guarantee that 6335 is absent, which is why V1 and the 6335 probe still apply. In a cluster you cannot bind it to `127.0.0.1`, because peers on other hosts must reach it, so bind it to the private cluster interface and firewall it to peers. TLS on the peer channel does not remove this requirement; turn it on as well, but it authenticates and encrypts the channel rather than making an exposed port safe to reach:

```yaml
cluster:
  p2p:
    enable_tls: true
```

`cluster.p2p.enable_tls` is separate from `service.enable_tls`: the first secures peer-to-peer traffic, the second the client API. Enabling `cluster.p2p.enable_tls` also requires a `ca_cert` in the `tls:` block, the CA that validates peer certificates; the security page marks `ca_cert: ./tls/cacert.pem` as required for peer TLS. Provision that CA and set the field before you enable peer TLS. Qdrant carries a compiled default path (`./tls/cacert.pem`), so a missing entry does not always fail at startup, but relying on an unprovisioned default is fragile and the vendor marks it required. Set both TLS settings in distributed mode, apply the configuration on every peer, and restart the peers one at a time. To rotate the client API key without downtime, set the new key as `service.alt_api_key` on each peer and restart one at a time; `alt_api_key` (available as of Qdrant v1.17.0) is an additional accepted client key and, like `api_key`, gates the client API; it reaches the internal channel only where `enforce_internal_auth` is set, on v1.18.0 and later. The peer-channel and rotation settings can be version-dependent, so confirm them against the security page for the Qdrant version you run.

## 3. Weaviate: disable anonymous access, then authorize

`AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED` defaults to `true`, which the Weaviate docs describe as strongly discouraged outside development. The secured Docker example:

```yaml
environment:
  AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
  AUTHENTICATION_APIKEY_ENABLED: 'true'
  AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'REPLACE_WITH_ADMIN_KEY,REPLACE_WITH_APP_KEY'
  AUTHENTICATION_APIKEY_USERS: 'admin-user,app-user'
  AUTHORIZATION_RBAC_ENABLED: 'true'
  AUTHORIZATION_RBAC_ROOT_USERS: 'admin-user'
```

Keys map to users by position, so the first key belongs to `admin-user` and the second to `app-user`. Only `admin-user` is a root user with full access; give `app-user` a custom role limited to its collections, created with the admin key through the RBAC API as the [RBAC configuration page](https://docs.weaviate.io/deploy/configuration/configuring-rbac) describes, and keep the admin key off the application host. Authentication alone lets any key holder do anything; add authorization with either RBAC (above, generally available from v1.29 per the authorization page) or the simpler admin list (`AUTHORIZATION_ADMINLIST_ENABLED`, `AUTHORIZATION_ADMINLIST_USERS`, `AUTHORIZATION_ADMINLIST_READONLY_USERS`; it cannot be combined with RBAC). For human logins, `AUTHENTICATION_OIDC_ENABLED` with `AUTHENTICATION_OIDC_ISSUER` and `AUTHENTICATION_OIDC_CLIENT_ID` delegates to an identity provider, where MFA is enforced ([mfa.md](mfa.md)). The documented deployment starts Weaviate with `--scheme http` and points to a reverse proxy for domain access, forwarding both 8080 and 50051; give the proxy the certificate ([free-certificates.md](free-certificates.md)) and do not expose the plain ports.

## 4. Milvus: enable authentication, change root, add TLS

For standalone Docker Compose at v2.6.24 and v3.0.2, the image reads `/milvus/configs/milvus.yaml`, but the supplied Compose file mounts only data at `/var/lib/milvus`. Editing a host-side configuration file alone changes nothing. The loader documents this file precedence, lowest to highest: `milvus.yaml`, `_test.yaml`, `default.yaml`, `user.yaml`. Use a small `user.yaml` to override the needed keys while retaining the image's other settings. These paths assume the image's `/milvus` working directory and no `MILVUSCONF` override, which selects a different configuration directory.

Create `./user.yaml` beside your Compose file with the authentication and TLS YAML below, and put the certificate files in `./tls/` before starting. Edit these mounts into the existing `standalone.volumes` list, keeping its data mount:

```yaml
services:
  standalone:
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/milvus:/var/lib/milvus
      - ./user.yaml:/milvus/configs/user.yaml:ro
      - ./tls:/milvus/tls:ro
```

Ensure the container account can read the configuration and certificate files and traverse their directories; keep the private key accessible only to that account and trusted administrators. The v3.0.2 Ubuntu image defaults to the `milvus` user. Alternatively, edit a complete `milvus.yaml` from the exact image version and mount it at `/milvus/configs/milvus.yaml:ro`; `user.yaml` still takes precedence. Recreate `standalone` after changing mounts or environment, and restart it after configuration or certificate changes before checking authentication and TLS.

Authentication is enabled by setting `common.security.authorizationEnabled: true` in `milvus.yaml` or the mounted `user.yaml` (or through the Helm `extraConfigFiles` / Operator `spec.config` equivalents). Once on, the built-in `root` user exists with the password `Milvus`; change it before exposure, since a documented default is a public credential ([authentication.md](authentication.md)):

```python
client = MilvusClient(uri="https://milvus.example.com:19530", token="root:Milvus")
client.update_password(user_name="root", old_password="Milvus", new_password="REPLACE_WITH_LONG_RANDOM_VALUE")
```

Create a per-application user rather than handing `root` to the app. Put both authentication and TLS in the same `user.yaml`, keeping a single `common` mapping:

```yaml
tls:
  serverPemPath: /milvus/tls/server.pem
  serverKeyPath: /milvus/tls/server.key
  caPemPath: /milvus/tls/ca.pem
common:
  security:
    authorizationEnabled: true
    tlsMode: 1      # 1 = server certificate only; 2 = mutual TLS, clients present a certificate too
```

Clients then connect with `secure=True` and the server certificate path. TLS and authentication are independent in Milvus; enable both.

The environment alternative at both tags is `COMMON_SECURITY_AUTHORIZATIONENABLED: "true"`, `COMMON_SECURITY_TLSMODE: "1"`, `TLS_SERVERPEMPATH: /milvus/tls/server.pem`, `TLS_SERVERKEYPATH: /milvus/tls/server.key` and `TLS_CAPEMPATH: /milvus/tls/ca.pem` under `standalone.environment`, retaining the certificate mount. The paramtable formatter lowercases names, strips a leading `milvus.`, then removes `/`, `_` and `.`; it does not strip a `MILVUS_` prefix. Per-key environment comments are not an allowlist. Choose one source for these settings and remove conflicting environment or remote configuration. The Compose files at these tags select older Milvus images, v2.6.23 and v3.0.1 respectively; explicitly select the intended image version and recheck its configuration when upgrading.

Milvus's internal component servers listen beyond 19530. In v3.0.2 and v2.6.24 (the latest 3.x and 2.6 releases checked), the proxy's internal port (19529), the query node (21123), the data node (21124), the mix coordinator (22125, the `rootCoord` port) and the streaming node (22222) each bind every interface: the listener is given only the port (and the query node, data node and streaming node fall back to a random port, still on every interface, when theirs is taken), and each component's `ip` setting is the address it advertises, not a bind address. Their gRPC interceptors check only routing metadata and pass a call that carries none, so these internal APIs, which include the query node's `Search` and `Query`, check no credentials; `authorizationEnabled` is enforced on the proxy's external client APIs, not on these internal ports. Internal TLS (`common.security.internaltlsEnabled`, off by default) is one-way, as Milvus's TLS documentation says: it encrypts the traffic but does not authenticate the caller, and if a component cannot load its certificate or key it logs a warning and serves plaintext. A standalone (or embedded) Milvus runs all five components, so keep every one of these ports reachable only by the Milvus deployment itself: publish only 19530 (with one exception for 9091, below), and only as section 1 describes (to loopback, or behind a reverse proxy, tunnel or tailnet), give Milvus a network of its own rather than attaching other workloads to it, do not run the container with host networking or share its network namespace with other workloads, and confine them with a default-deny network policy (on Kubernetes) or a default-deny host firewall (for a native, embedded or single-host install too) that admits only the traffic you intend, admitting Milvus peers by source (by pod selector in a network policy, by address in a host firewall) rather than by port, so other hosts are refused on the random fallback ports as well as on these port numbers. Neither control reliably stops processes on the same machine: a local process can reach a native install over loopback and a container or pod directly at its own address, and a Kubernetes NetworkPolicy always allows traffic between a pod and the node it runs on. So keep untrusted workloads and users off every host that runs a Milvus component, Kubernetes nodes included.

Milvus's standalone `docker-compose.yml` publishes more than Milvus itself: it maps its bundled MinIO object store to the host on `9000` (S3 API) and `9001` (console) on every interface, beside the Milvus ports above, while etcd stays on the internal network. Give those two ports the same treatment as Milvus's own: loopback-map or firewall them off the public mapping, and change MinIO's default login, since authenticating Milvus does nothing for a MinIO published next to it ([minio.md](minio.md)).

Rotate the storage credentials on both services together. At both checked tags, Compose selects `minio/minio:RELEASE.2024-05-28T17-19-04Z` and supplies `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY`, both `minioadmin`, to **MinIO**. **Milvus** reads `MINIO_ACCESS_KEY_ID` and `MINIO_SECRET_ACCESS_KEY`, mapping to `minio.accessKeyID` and `minio.secretAccessKey`, also defaulting to `minioadmin`. For the bundled login, the access-key values must match across services and the secret-key values must match; changing MinIO alone leaves Milvus using the old credentials. These are the names in this pinned Compose file, not a claim about newer MinIO images' `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` support. For a dedicated Milvus application key, use its own matching pair with access to Milvus's storage, following [minio.md](minio.md).

Keep the values in private, untracked env-files: `./.env.minio` with `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY`, and `./.env.milvus-storage` with `MINIO_ACCESS_KEY_ID` and `MINIO_SECRET_ACCESS_KEY`. Use `NAME=value` lines, single-quoting values where Compose interpolation would change a literal dollar sign. Make both files owner-only (mode `0600`) in a private directory and exclude them from version control before adding credentials ([secrets.md](secrets.md)). Delete MinIO's two existing credential entries from `environment:` in the vendor Compose file, since `environment:` overrides `env_file`, then add this excerpt to the existing services:

```yaml
services:
  minio:
    env_file: ./.env.minio
  standalone:
    env_file: ./.env.milvus-storage
```

Keep `standalone.environment`'s `ETCD_ENDPOINTS`, `MINIO_ADDRESS` and `MINIO_REGION`. Recreate both services after rotating the env-files; a restart alone does not replace container environment values. Env-files keep literal secrets out of Compose YAML, but the values remain in container environment data, visible to Docker administrators through inspection and potentially in diagnostic output. Treat rendered Compose configuration and inspection output as sensitive. Compose secrets require application support for reading mounted files; do not invent `MINIO_SECRET_ACCESS_KEY_FILE` for Milvus ([docker.md](docker.md)).

In v2.6.24 and v3.0.2, the management/metrics HTTP listener (9091 by default) also serves control routes that check no credentials; `common.security.authorizationEnabled` covers only the proxy's `/api/v1` routes on the same port. The routes named here are representative, not a full list. Every Milvus server process serves `/log/level`, which reads or changes the log level, and, after its components' startup calls return successfully, `/management/stop`, which stops a role running in that process. A process running the proxy adds routes that pause and resume garbage collection, suspend and resume query nodes and balancing, and transfer segments and channels, plus `/management/rootcoord/ez/backup`, which returns a named database's encryption-zone key backup (`ezk`) in its response where a cipher plugin supports it; v3.0.2 adds routes that clear queued reads and commit backfill results from a caller-supplied path. An activated mix coordinator adds its own garbage-collection, balancing, node-suspension and transfer routes, and routes that alter mutable configuration (`/management/config/alter`) and change the WAL backend. A standalone process runs both. With `proxy.http.enablePprof` at its default `true` at startup, the same listener also serves Go's `/debug/pprof/` profiling handlers. The first request to `/eventlog` that successfully creates it starts a further gRPC listener, with no authentication or TLS, on a random port on every interface of the process's network namespace. Setting `proxy.http.enableWebUI: false` before startup omits the UI but leaves every one of these controls, and setting `proxy.http.enablePprof: false` before startup leaves out the profiling handlers while the control routes are still registered. The listener binds every interface in its network namespace, with no bind-address flag, config key or environment variable. `METRICS_PORT` changes only its port: a value `strconv.Atoi` rejects (unset, empty, non-numeric, or an integer too large for it) falls back to 9091, `0` takes a random port, and any other parsed value outside 1 to 65535 makes the listen fail, which Milvus logs without stopping. The standalone Compose files at those tags publish `9091:9091`, which binds every host interface under Docker's default publishing settings (the files select v2.6.23 and v3.0.1 images respectively). Delete that mapping: the in-container `http://localhost:9091/healthz` probe does not need it, and the rule above is to publish only 19530. If an administrator on the Docker host needs the listener, the one exception is a loopback-only mapping, `127.0.0.1:9091:9091`, firewalled from everyone else. If you choose another fixed `METRICS_PORT`, set it under the `standalone` service's `environment:`, since the Compose files do not pass it through from your shell, and adjust the container port in any mapping and in the healthcheck. Retain the network and host isolation above: loopback publication does not isolate the container from same-network peers or local users; see [docker.md](docker.md) for publication and firewall caveats. How the Helm chart and the Operator expose 9091 was not checked; backlog row 1.149 tracks it.

## 5. Chroma: no native authentication since 1.0

Chroma's migration notes for v1.0.0 state that "Chroma no longer provides built-in authentication implementations". A self-hosted `chroma run --path /db_path` server (port 8000) therefore accepts every request, and the older `CHROMA_SERVER_AUTHN_PROVIDER` / `CHROMA_SERVER_AUTHN_CREDENTIALS` variables from the 2024 auth overhaul no longer do anything; do not paste them from old tutorials and assume protection. Keep Chroma on loopback and expose it only through an authenticated TLS proxy (bearer-token or basic-auth block per [nginx.md](nginx.md) / [caddy.md](caddy.md)), a Cloudflare Tunnel with Access ([cloudflare.md](cloudflare.md)), or a tailnet ([tailscale.md](tailscale.md)).

## 6. pgvector: it is PostgreSQL

pgvector is an extension (`CREATE EXTENSION vector;`, PostgreSQL 13 and later), so [postgresql.md](postgresql.md) applies unchanged: `ssl = on`, `hostssl` lines with `scram-sha-256`, a least-privilege role per application, and `sslmode=verify-full` in every connection string. When several tenants share one embeddings table, add row-level security keyed on the tenant column so a query can only match rows the connected role may see.

## 7. Hosted services and MFA

Pinecone, Qdrant Cloud, Weaviate Cloud, and Zilliz authenticate with API keys: those are secrets under [secrets.md](secrets.md), one per environment, never committed, rotated on leak. The vendor terminates TLS, so the client-side check is that the SDK is pointed at the `https://` endpoint the console gives you. None of the self-hosted servers has a human login with a second factor; MFA exists only on the vendor console for the hosted tiers, at the identity provider when Weaviate uses OIDC, or on the fronting layer (Access policy, Authelia-style portal) for everything else ([mfa.md](mfa.md)).

## Verify

Inventory every listener without grep, because filtering for the ports you expect hides the listener you did not (a grep for `6333` also matches a port `63330` or a PID). Read the whole table:

```bash
# REASONED: listener expectations follow the cited Qdrant documentation; no distributed Qdrant cluster is available.
sudo ss -tulnp                       # read every row; any 6333/6334/6335 on a wildcard
                                     # (0.0.0.0, *, [::]) or public address fails bind-privately.
                                     # In a container, also run it in the container netns and check
                                     # published ports; the host table alone does not show -p 6335:6335.
```

Then probe each Qdrant backend port from a host **outside** the peer allowlist, against the node's real address, running the block three times with `6333`, `6334`, then `6335` on the `set --` line. **These probes are reasoned, not demonstrated** (no distributed Qdrant cluster in the authoring environment; expected outcomes follow the cited Qdrant documentation). Bracket an IPv6 literal, for example `'[2001:db8::1]'`; `-g` keeps curl from globbing the brackets. The block prints the `exitcode` and `errormsg` write-out variables, which need curl 7.75.0 or newer:

```bash
# REASONED: backend reachability follows the cited Qdrant documentation; no distributed Qdrant cluster is available.
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST_ADDRESS' 'REPLACE_WITH_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then echo "substitute the values on the set -- line above; not probing"; exit; fi
  case "$1:$2" in
    *REPLACE_WITH_*|*[[:cntrl:]]*) echo "substitute the values on the set -- line above; not probing"; exit ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:$2/"
)
```

Read the exit code and the elapsed time together (curl's exit strings vary by version, so key on the code, not the message). A non-peer probe of a restricted 6335 should FAIL TO CONNECT: curl reports `exit=7` (the TCP connection did not complete, whether refused or reset), or `exit=28` at about 5 seconds (the connect timeout, consistent with a firewall that drops the packet). Neither proves the port is closed on its own, so corroborate with the inventory and the filtering point's own deny evidence. Two other exits are your own input error, not a result: `exit=6` (could not resolve host) means you mistyped the address, and `exit=3` (a malformed URL) means the target string is wrong; fix the value and re-run. Any sign the connection COMPLETED is a reachability fail for a backend port from a non-peer: a non-zero `http=` status, `exit=52` (empty reply) or `exit=56` (receive failure), or `exit=28` at about 20 seconds (the max-time, the connection opened and then stalled). Do not judge on `http=` alone: curl prints `http=000` both when nothing connected and when a connection completed with no HTTP response, so pair it with the exit code, since a `52` or `56` alongside `000` is still a completed connection and a fail. A key check or a TLS rejection after the connection opens does not un-expose the port. Plaintext `http://` is deliberate: the question is only whether the TCP connection completed, and a plaintext probe that reaches a TLS-only peer port still completes the TCP connection and surfaces as one of the reachable signals above.

For 6335 specifically, in distributed mode, require two results. From a non-peer: a failure to connect, `exit=7` or a 5-second `exit=28`, corroborated by the inventory and firewall evidence (a `exit=6` or `exit=3` is a mistyped target, not a result). From an allowed peer: POSITIVE evidence that the connection completed, a non-zero `http=` status (not `http=000`, which curl prints when nothing was received), or a post-connect exit (`52`, `56`, or the 20-second `exit=28`), not merely the absence of a refusal, because a mistyped target also avoids `exit=7`. The pair separates "restricted to peers, cluster works" from both "exposed to everyone" and "blocked for everyone". 6335 absent from the inventory is consistent with single-node but does not prove it can never appear, so probe it anyway.

Keep the existing client-API key check, hardened, against the frontend hostname over TLS (never a backend IP, never `curl -k`, which a gate rejects). It confirms the key is enforced, but it **cannot** distinguish a keyed single-node deployment from a keyed distributed one with 6335 exposed, because both answer 401 then 200; only the port probes above catch an exposed 6335:

REASONED: following block; client-key outcomes follow the cited Qdrant security documentation; no live frontend outcome is recorded in this guide.

```bash
(                              # a subshell, so your own script arguments are untouched
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The API key (REPLACE_WITH_LONG_RANDOM_VALUE) on the set -- line enters shell
  # history. Use a short-lived key or clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_FRONTEND_HOSTNAME' 'REPLACE_WITH_LONG_RANDOM_VALUE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then echo "substitute the values on the set -- line above; not probing"; exit; fi
  case "$1:$2" in
    *REPLACE_WITH_*|*[[:cntrl:]]*) echo "substitute the values on the set -- line above; not probing"; exit ;;
  esac
  echo "without key (expect http=401 or 403):"
  curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1/collections"
  echo "with key (expect http=200):"
  printf 'api-key: %s\n' "$2" | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
    -H @- \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1/collections"
)
```

**Exposed:** without-key returns `http=200` (no key, or a proxy that does not enforce it), or a backend port is reachable from a non-peer. **Fixed:** without-key returns `401`/`403` and with-key returns `200`, and 6335 is refused from a non-peer while a peer connects.

For Weaviate and Chroma, the fronted client checks still apply:

REASONED: following block; Weaviate authentication and Chroma migration documentation distinguish native and fronting authorization; no live outcomes for these frontends are recorded.

```bash
# --noproxy '*' so a forward proxy's CONNECT "200 Connection established" cannot masquerade as the
# service status; -w prints the real code and exit, and -g keeps curl from globbing a substitution.
curl -q -g -sS --noproxy '*' -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' https://weaviate.example.com/v1/schema
                                     # without a key: expect http=401 (Weaviate) or the fronting proxy's 401/403
curl -q -g -sS --noproxy '*' -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' https://chroma.example.com/
                                     # Chroma has no native auth: expect the proxy's 401/403, never a Chroma http=200
# Positive control: a 401/403 above proves denial, not that authorized access works, so confirm an
# authorized request succeeds (and satisfy any auth the fronting proxy also requires). For Chroma,
# which has no native auth, verify authorized access through the fronting proxy instead.
curl -q -g -sS --noproxy '*' -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  -H @REPLACE_WITH_AUTH_HEADER_FILE https://weaviate.example.com/v1/schema
                                     # with a valid key (Authorization header read from a file): expect http=200
```

For Milvus, a `MilvusClient(uri=...)` call with no `token` must fail once `authorizationEnabled` is on, and the same call with the application user's credentials must succeed.

Client authentication does not cover Milvus's management listener (section 4), so probe it separately. Run the backend-port block above with `9091` on its `set --` line, from a host outside your administrators' network, against the node's real address, and read it by the rules given for 6335: any sign the connection completed is a fail. Where you kept the loopback-only mapping, run it again on the Docker host against `127.0.0.1`: a completed connection there is the positive control for that mapping. With the mapping deleted, as recommended, the positive control has two parts, both inside the container. `docker compose ps` must show the `standalone` service as `healthy`, which means its in-container `curl -f http://localhost:9091/healthz` got a non-error answer. The `ss -tulnp` inventory, run in the container's network namespace, must also show that port held by the `milvus` process, because `healthy` alone says only that something answered there: another process in the namespace could hold the port, and `/healthz` can answer before every component has registered. A failed bind is only logged and Milvus keeps running, so a refused probe from outside proves nothing on its own. With a different `METRICS_PORT`, read that port in both checks. The `/eventlog` listener has no fixed port, so find any other port the Milvus process holds in the `ss -tulnp` inventory above, run inside the container's network namespace as well, and probe those ports the same way. A port missing from the inventory was only missing when you looked: the listener is created on the first request, so repeat the inventory after anything has called `/eventlog`. These probes are reasoned, not demonstrated (no Milvus deployment or container runtime in the authoring environment); expected outcomes follow the pinned v2.6.24 and v3.0.2 sources cited for the management listener.

None of the checks above tests isolation between tenants. Where one embeddings table serves several users or tenants under the row-level security above, prove the boundary as well as the ports: connect as the role for tenant B, run the similarity search tenant A would run, and confirm only tenant B's rows come back. For the positive control, run the same query as a role that bypasses the policy (a superuser or a role with `BYPASSRLS`; the table owner also bypasses unless the table has `FORCE ROW LEVEL SECURITY`) and confirm tenant A's rows now appear. Count rows per tenant, or drop the `LIMIT`, rather than trusting the top-k result: the nearest neighbours of tenant A's query vector can legitimately all be tenant A's rows even with the policy off, so an empty other-tenant result there does not by itself prove the policy is filtering. A query that returns another tenant's vectors under tenant B's own role is a live cross-user leak, whatever the network posture. This isolation check is reasoned, not demonstrated: the authoring environment has no live multi-tenant pgvector table to run it against; expected outcomes follow the cited PostgreSQL row-security documentation.

## Sources (checked September 2026)

- Milvus Compose configuration and credentials (v2.6.24, pinned commit): image paths, file precedence, environment formatter, authentication/TLS keys and storage defaults: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/deployments/docker/standalone/docker-compose.yml#L21-L32, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/build/docker/milvus/ubuntu22.04/Dockerfile#L37, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/base_table.go#L69-L72, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/base_table.go#L145-L153, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/base_table.go#L248-L264, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/component_param.go#L974-L979, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/grpc_param.go#L112-L139, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/service_param.go#L1452-L1477
- Milvus Compose configuration and credentials (v3.0.2, pinned commit): image paths, the image's runtime user (`USER ${MILVUS_RUNTIME_USER}`, default `milvus:milvus`), file precedence, environment formatter, authentication/TLS keys and storage defaults: https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/deployments/docker/standalone/docker-compose.yml#L21-L32, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/build/docker/milvus/ubuntu22.04/Dockerfile#L39, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/build/docker/milvus/ubuntu22.04/Dockerfile#L58-L59, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/build/docker/milvus/ubuntu22.04/Dockerfile#L16, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/base_table.go#L69-L72, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/base_table.go#L145-L153, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/base_table.go#L249-L265, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/component_param.go#L1046-L1051, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/grpc_param.go#L111-L138, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/service_param.go#L1633-L1658
- Docker Compose env-files and environment precedence, read-only mounts, and secrets as files requiring image support: https://docs.docker.com/reference/compose-file/services/#env_file, https://docs.docker.com/reference/compose-file/services/#volumes and https://docs.docker.com/compose/how-tos/use-secrets/
- Kubernetes NetworkPolicy, "traffic to and from the node where a Pod is running is always allowed, regardless of the IP address of the Pod or the node": https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Milvus internal listeners (pinned tag v3.0.2): the listener that binds only the port, each component's listener, routing-only interceptors and internal-TLS option (query node, data node, streaming node, mix coordinator, proxy internal port), the interceptors that pass calls without metadata, one-way internal TLS, the default ports with `authorizationEnabled` and `internaltlsEnabled` off, standalone enabling all five components, the query node's `Search` and `Query`, `credentials.NewServerTLSFromFile` returning nil credentials with the load error and otherwise building a `tls.Config` that sets only the server certificate, requiring no client certificate (grpc-go v1.82.2, the version in go.mod), because `tls.Config.ClientAuth` defaults to `NoClientCert`, the zero value of `ClientAuthType` (Go standard library go1.26.6, the go directive in go.mod), and gRPC serving plaintext when the credentials are nil: https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/netutil/listener.go#L11-L35, https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/netutil/listener.go#L92-L103, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/querynode/service.go#L123-L126, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/querynode/service.go#L246, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/querynode/service.go#L243-L253, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/querynode/service.go#L268, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/datanode/service.go#L82-L85, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/datanode/service.go#L127, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/datanode/service.go#L148, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/streamingnode/service.go#L106-L109, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/streamingnode/service.go#L345, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/streamingnode/service.go#L355, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/mixcoord/service.go#L97-L100, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/mixcoord/service.go#L212, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/mixcoord/service.go#L234, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/proxy/listener_manager.go#L56-L58, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/proxy/service.go#L461, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/proxy/service.go#L482, https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/interceptor/cluster_interceptor.go#L34-L48, https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/util/interceptor/server_id_interceptor.go#L36-L54, https://github.com/milvus-io/milvus/blob/v3.0.2/internal/distributed/utils/util.go#L39-L63, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L357, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L457, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L458, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L690, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L978, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L1155-L1162, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L1165, https://github.com/milvus-io/milvus/blob/v3.0.2/configs/milvus.yaml#L1442, https://github.com/milvus-io/milvus/blob/v3.0.2/cmd/milvus/util.go#L142-L147, https://github.com/milvus-io/milvus/blob/v3.0.2/pkg/proto/query_coord.proto#L109-L147, https://github.com/grpc/grpc-go/blob/v1.82.2/credentials/tls.go#L302-L308, https://github.com/grpc/grpc-go/blob/v1.82.2/credentials/tls.go#L222-L257, https://github.com/golang/go/blob/go1.26.6/src/crypto/tls/common.go#L348-L354, https://github.com/golang/go/blob/go1.26.6/src/crypto/tls/common.go#L698-L700 and https://github.com/grpc/grpc-go/blob/v1.82.2/internal/transport/http2_server.go#L151-L167
- Milvus internal listeners (pinned tag v2.6.24): the listener that binds only the port, each component's listener, routing-only interceptors and internal-TLS option (query node, data node, streaming node, mix coordinator, proxy internal port), the interceptors that pass calls without metadata, one-way internal TLS, the default ports with `authorizationEnabled` and `internaltlsEnabled` off, standalone enabling all five components, the query node's `Search` and `Query`, `credentials.NewServerTLSFromFile` returning nil credentials with the load error and otherwise building a `tls.Config` that sets only the server certificate, requiring no client certificate (grpc-go v1.82.1, the version in go.mod), because `tls.Config.ClientAuth` defaults to `NoClientCert`, the zero value of `ClientAuthType` (Go standard library go1.25.8, the go directive in go.mod), and gRPC serving plaintext when the credentials are nil: https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/netutil/listener.go#L11-L35, https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/netutil/listener.go#L92-L103, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/querynode/service.go#L93-L96, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/querynode/service.go#L190, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/querynode/service.go#L187-L197, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/querynode/service.go#L212, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/datanode/service.go#L83-L86, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/datanode/service.go#L128, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/datanode/service.go#L149, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/streamingnode/service.go#L108-L111, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/streamingnode/service.go#L352, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/streamingnode/service.go#L362, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/mixcoord/service.go#L99-L102, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/mixcoord/service.go#L214, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/mixcoord/service.go#L236, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/proxy/listener_manager.go#L58-L60, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/proxy/service.go#L441, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/proxy/service.go#L461, https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/interceptor/cluster_interceptor.go#L34-L48, https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/util/interceptor/server_id_interceptor.go#L36-L54, https://github.com/milvus-io/milvus/blob/v2.6.24/internal/distributed/utils/util.go#L41-L66, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L309, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L396, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L397, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L623, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L880, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L1036-L1043, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L1046, https://github.com/milvus-io/milvus/blob/v2.6.24/configs/milvus.yaml#L1322, https://github.com/milvus-io/milvus/blob/v2.6.24/cmd/milvus/util.go#L143-L148, https://github.com/milvus-io/milvus/blob/v2.6.24/pkg/proto/query_coord.proto#L107-L145, https://github.com/grpc/grpc-go/blob/v1.82.1/credentials/tls.go#L302-L308, https://github.com/grpc/grpc-go/blob/v1.82.1/credentials/tls.go#L222-L257, https://github.com/golang/go/blob/go1.25.8/src/crypto/tls/common.go#L335-L341, https://github.com/golang/go/blob/go1.25.8/src/crypto/tls/common.go#L681-L683 and https://github.com/grpc/grpc-go/blob/v1.82.1/internal/transport/http2_server.go#L151-L167
- Milvus TLS documentation, internal TLS "For now only one-way tls is supported" (milvus-docs pinned commit cee60f10e2b794fbaf9bd6a02d5f129335218dfa): https://github.com/milvus-io/milvus-docs/blob/cee60f10e2b794fbaf9bd6a02d5f129335218dfa/site/en/adminGuide/tls.md#L215
- Qdrant security (API key, read-only key, `api-key` header, TLS keys, ports, default insecurity): https://qdrant.tech/documentation/security/
- Qdrant compiled-in defaults and overlay order (`service.host`, `http_port`, `grpc_port`; `config/config`, `config/$RUN_MODE` defaulting to `development`, `config/local`, `/etc/qdrant/config` in `deb` builds, `--config-path`, `QDRANT__` variables), the development and production overlays, and the image's `RUN_MODE=production` with an entrypoint that runs `./qdrant $@`, and the release workflow that builds `qdrant/qdrant` from the root `Dockerfile` (pinned tag v1.19.1): https://github.com/qdrant/qdrant/blob/v1.19.1/src/settings.rs#L22, https://github.com/qdrant/qdrant/blob/v1.19.1/src/settings.rs#L292-L329, https://github.com/qdrant/qdrant/blob/v1.19.1/config/config.yaml#L330-L334, https://github.com/qdrant/qdrant/blob/v1.19.1/config/config.yaml#L352, https://github.com/qdrant/qdrant/blob/v1.19.1/config/development.yaml#L13-L15, https://github.com/qdrant/qdrant/blob/v1.19.1/config/production.yaml#L3-L5, https://github.com/qdrant/qdrant/blob/v1.19.1/Dockerfile#L225-L246, https://github.com/qdrant/qdrant/blob/v1.19.1/tools/entrypoint.sh#L21 and https://github.com/qdrant/qdrant/blob/v1.19.1/.github/workflows/docker-image.yml#L47-L55
- Weaviate authentication (anonymous access, API key, OIDC variables): https://docs.weaviate.io/deploy/configuration/authentication
- Weaviate authorization (admin list, RBAC availability): https://docs.weaviate.io/deploy/configuration/authorization and RBAC configuration (`AUTHORIZATION_RBAC_ENABLED`, `AUTHORIZATION_RBAC_ROOT_USERS`): https://docs.weaviate.io/deploy/configuration/configuring-rbac
- Weaviate environment variables (`AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED` default, `GRPC_PORT` default): https://docs.weaviate.io/deploy/configuration/env-vars
- Weaviate Docker installation (ports 8080/50051, `--scheme http`, reverse proxy layout): https://docs.weaviate.io/deploy/installation-guides/docker-installation
- Weaviate REST `--host`/`--port` and their `HOST`/`PORT` variables, the REST listen call, the gRPC listener, started unconditionally, on `:<GRPC_PORT>` with no host field in its configuration and its 50051 default, the debug listener on `:<GO_PROFILING_PORT>` (default 6060) with its disable switch and 404 gate, the Prometheus listener on `:<port>` (2112 when enabled from the environment), and the image's `--host 0.0.0.0 --port 8080`, built by `ci/push_docker.sh` from the root `Dockerfile`'s `weaviate` target (pinned tag v1.39.6), with go-flags v1.6.1 reading `HOST` through `os.LookupEnv`, so an empty value replaces the default: https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L89-L90, https://github.com/jessevdk/go-flags/blob/v1.6.1/option.go#L328-L343, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L569, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L2613-L2657, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/handlers_debug_gate.go#L23-L33, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L329-L336, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L502-L509, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L223-L275, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L95-L98, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L377, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L1664, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/grpc.go#L27-L33, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/grpc/server.go#L475-L477, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/config_handler.go#L947-L955, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L1050-L1054, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L2029, https://github.com/weaviate/weaviate/blob/v1.39.6/Dockerfile#L57-L63, https://github.com/weaviate/weaviate/blob/v1.39.6/ci/push_docker.sh#L5, https://github.com/weaviate/weaviate/blob/v1.39.6/ci/push_docker.sh#L114 and https://github.com/weaviate/weaviate/blob/v1.39.6/ci/push_docker.sh#L131
- Weaviate's configuration precedence (config file, then environment, then flags), REST schemes (`--scheme`, default from the API spec's `https`) and the fatal exit when `https` has no certificate, the Prometheus port variable, the TLS listener's `--tls-host`/`TLS_HOST` falling back to `--host` and `--tls-port`/`TLS_PORT`, `--socket-path`, and its cluster listeners: gossip bind address and ports, the data port default, Raft and its RPC port defaults and bind address, the unconditional cluster init and cluster API server (pinned tag v1.39.6), with memberlist v0.5.4's `0.0.0.0:7946` default, its TCP and UDP listeners and its private advertise address: https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L47-L53, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L81, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L149-L160, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L86, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L97-L100, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L303-L310, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/embedded_spec.go#L39-L41, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/config_handler.go#L1305-L1340, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/config_handler.go#L1371-L1377, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/server.go#L345-L349, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L37-L38, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L1898-L1914, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L1926-L1942, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L733-L736, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/config_handler.go#L1333-L1336, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L1736-L1739, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L320-L326, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L1617-L1627, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L2059-L2061, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/config/environment.go#L2145-L2188, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/cluster/state.go#L431-L446, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/cluster/state.go#L662-L673, https://github.com/weaviate/weaviate/blob/v1.39.6/usecases/cluster/state.go#L695-L705, https://github.com/weaviate/weaviate/blob/v1.39.6/cluster/store.go#L591-L592, https://github.com/weaviate/weaviate/blob/v1.39.6/cluster/service.go#L152, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L636, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L822-L823, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/configure_api.go#L1804, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/clusterapi/serve.go#L47-L49, https://github.com/weaviate/weaviate/blob/v1.39.6/adapters/handlers/rest/clusterapi/serve.go#L140, https://github.com/weaviate/weaviate/blob/v1.39.6/go.mod#L54, https://github.com/hashicorp/memberlist/blob/v0.5.4/config.go#L302-L307, https://github.com/hashicorp/memberlist/blob/v0.5.4/net_transport.go#L96-L110 and https://github.com/hashicorp/memberlist/blob/v0.5.4/net_transport.go#L140-L160
- Milvus authentication (`common.security.authorizationEnabled`, default `root`/`Milvus`, `update_password`): https://milvus.io/docs/authenticate.md
- Milvus TLS (`tls.*` paths, `common.security.tlsMode`, RESTful port note): https://milvus.io/docs/tls.md
- Milvus management HTTP listener, v2.6.24 (commit 08c637c14373ec904dcac08e4df67279de421917): default port, direct log-level and stop handlers, conditional WebUI, mux without authentication, wildcard bind and METRICS_PORT parsing; process startup and stop callback; available flags: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/server.go#L38-L40, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/server.go#L77-L120, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/server.go#L215-L260, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/cmd/roles/roles.go#L458-L459, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/cmd/roles/roles.go#L529-L544 and https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/cmd/milvus/util.go#L124-L199
- Milvus management HTTP listener, v3.0.2 (commit 3c4448a2aee506ccd14851e742aba85f1c83188a): the same controls and listener inputs: https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/server.go#L37-L39, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/server.go#L82-L127, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/server.go#L230-L275, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/cmd/roles/roles.go#L500-L501, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/cmd/roles/roles.go#L575-L590 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/cmd/milvus/util.go#L123-L198
- Milvus control and profiling routes on the same listener, v2.6.24 (commit 08c637c14373ec904dcac08e4df67279de421917) and v3.0.2 (commit 3c4448a2aee506ccd14851e742aba85f1c83188a): the proxy's management routes, registered with no credential check, the encryption-zone key backup among them, and the two v3.0.2 additions: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/proxy/management.go#L42-L97, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/proxy/management.go#L594-L620, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L42-L105, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L198-L244, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L427-L447 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/proxy/management.go#L700-L726; the mix coordinator's routes, registered on activation, including the node-status `PUT` that suspends or resumes a query node: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/restful_mgr_routes.go#L36-L74, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/restful_mgr_routes.go#L881-L890, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/restful_mgr_routes.go#L943-L1010, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/coordinator/mix_coord.go#L237-L240, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/restful_mgr_routes.go#L33-L71, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/restful_mgr_routes.go#L878-L887, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/restful_mgr_routes.go#L940-L1007 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/coordinator/mix_coord.go#L242-L245; `authorizationEnabled` applied to the proxy's `/api/v1` group only: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/distributed/proxy/service.go#L169-L186 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/distributed/proxy/service.go#L168-L185; the pprof import and its default: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/metrics/metrics.go#L21, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/metrics/metrics.go#L21, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/util/paramtable/http_param.go#L71-L78 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/util/paramtable/http_param.go#L76-L83; the event-log listener: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/eventlog/grpc.go#L113-L146 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/eventlog/grpc.go#L113-L146; `strconv.Atoi` range errors: https://pkg.go.dev/strconv#Atoi
- Milvus encryption-zone key backup and event-log handler, v2.6.24 (commit 08c637c14373ec904dcac08e4df67279de421917) and v3.0.2 (commit 3c4448a2aee506ccd14851e742aba85f1c83188a): the backup refuses a database that is not an encryption zone and returns the plugin's backup otherwise: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/rootcoord/root_coord.go#L3180-L3219, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/util/hookutil/cipher.go#L390-L401, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/util/hookutil/ez.go#L113-L125, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/rootcoord/root_coord.go#L3464-L3503, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/util/hookutil/cipher.go#L389-L400 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/util/hookutil/ez.go#L113-L125; the `/eventlog` handler creating the listener on request: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/eventlog/handler.go#L50-L65 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/eventlog/handler.go#L48-L63; the Compose service's environment, which does not pass `METRICS_PORT`, and its healthcheck: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/deployments/docker/standalone/docker-compose.yml#L39-L66 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/deployments/docker/standalone/docker-compose.yml#L39-L66
- Milvus `/healthz` handler, v2.6.24 (commit 08c637c14373ec904dcac08e4df67279de421917) and v3.0.2 (commit 3c4448a2aee506ccd14851e742aba85f1c83188a): it answers 500 while any registered component is neither healthy nor on standby, and 200 otherwise, including before any component has registered: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/internal/http/healthz/healthz_handler.go#L89-L130 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/internal/http/healthz/healthz_handler.go#L87-L128; curl's `--fail` exit on an HTTP error (rolling documentation, checked September 2026): https://curl.se/docs/manpage.html#-f; Docker's health status from the check's exit code: https://docs.docker.com/reference/dockerfile/#healthcheck
- Milvus standalone Compose at v2.6.24 and v3.0.2: selected image tags, standalone command, localhost healthcheck, explicit publications of 19530 and 9091, and default network: https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/deployments/docker/standalone/docker-compose.yml#L39-L66 and https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/deployments/docker/standalone/docker-compose.yml#L39-L66
- Milvus log-level handler dependency (zap v1.27.0, GET reads and PUT changes the level): https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/pkg/log/log.go#L278-L280, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/pkg/mlog/level.go#L72-L74, https://github.com/milvus-io/milvus/blob/08c637c14373ec904dcac08e4df67279de421917/go.mod#L47, https://github.com/milvus-io/milvus/blob/3c4448a2aee506ccd14851e742aba85f1c83188a/go.mod#L43 and https://github.com/uber-go/zap/blob/v1.27.0/http_handler.go#L69-L103
- Docker port publication: default host binding, explicit loopback mapping, same-network and host access, direct-routing and older-engine caveats: https://docs.docker.com/engine/network/port-publishing/
- Chroma migration notes (v1.0.0 removal of built-in authentication; 2024 auth overhaul variables): https://docs.trychroma.com/docs/overview/migration ; client-server mode (`chroma run --path`, port 8000): https://docs.trychroma.com/docs/run-chroma/client-server
- Chroma `chroma run`: the `--host` default `localhost` applied only without a config file, the config-file branch, the `listen_address` and `port` defaults `0.0.0.0` and 8000, `CHROMA_` variables merged when a file is loaded, the server's bind of `listen_address:port`, and the release image (`rust/Dockerfile` target `cli`, `chroma run /config.yaml` from `docker_single_node.yaml`) (pinned tag 1.5.9): https://github.com/chroma-core/chroma/blob/1.5.9/rust/cli/src/commands/run.rs#L39-L45, https://github.com/chroma-core/chroma/blob/1.5.9/rust/cli/src/commands/run.rs#L60-L73, https://github.com/chroma-core/chroma/blob/1.5.9/rust/cli/src/commands/run.rs#L114-L134, https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/config.rs#L140-L146, https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/config.rs#L176-L179, https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/config.rs#L216-L229, https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/src/server.rs#L415-L417, https://github.com/chroma-core/chroma/blob/1.5.9/rust/Dockerfile#L85-L93, https://github.com/chroma-core/chroma/blob/1.5.9/rust/frontend/sample_configs/docker_single_node.yaml and https://github.com/chroma-core/chroma/blob/1.5.9/.github/workflows/_build_release_container.yml#L101-L106
- pgvector (`CREATE EXTENSION vector`, PostgreSQL 13 and later): https://github.com/pgvector/pgvector
- PostgreSQL row security policies (a superuser and a `BYPASSRLS` role always bypass; the table owner bypasses unless the table has `FORCE ROW LEVEL SECURITY`): https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0; rolling documentation, checked September 2026): https://curl.se/docs/manpage.html
