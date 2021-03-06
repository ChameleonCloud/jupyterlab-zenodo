import { Token } from '@lumino/coreutils';

export class ZenodoConfig {
  readonly baseUrl: string;
  readonly externalEditUrl: string;
}

export class ZenodoRecord {
  readonly doi: string;
  readonly path: string;
}

export class ZenodoFormFields {
  readonly title?: string;
  readonly author?: string;
  readonly affiliation?: string;
  readonly description?: string;
  readonly directory?: string;
  readonly zenodoToken?: string;
}

/* tslint:disable */
export const IZenodoRegistry = new Token<IZenodoRegistry>(
  '@jupyterlab_zenodo:IZenodoRegistry'
)
/* tslint:enable */

export interface IZenodoRegistry {
  newDepositionVersion(path: string): Promise<ZenodoRecord>;
  createDeposition(path: string, post: ZenodoFormFields): Promise<ZenodoRecord>;
  getDepositions(): Promise<ZenodoRecord[]>;
  getDeposition(path: string): Promise<ZenodoRecord>;
  hasDepositionSync(path: string): boolean;
  getDepositionSync(path: string): ZenodoRecord | undefined;
}
